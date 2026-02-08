"""
Resilient Data Pipeline for Tactics

Uses the resilient database layer for fault-tolerant operation:
- Continues working with cached data when Supabase is unavailable
- Queues failed writes for automatic retry
- Supports both Core and Enterprise tier algorithms
"""

import os
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, Literal
from enum import Enum

# Resilient database layer (preferred)
from .database_resilient import (
    get_ventas, get_gastos, get_company_tokens,
    save_insights_jsonb, save_predictions, save_mmm_results,
    check_database_health, process_retry_queue, get_local_cache
)

# Connectors
from .connectors import sync_shopify, sync_meta_ads

# Core algorithms
from core.segmentation import segment_customers
from core.optimizer import BudgetOptimizer
from core.resilience import DataGuard
from core.secure_vault import SecureVault


class PipelineTier(str, Enum):
    CORE = "core"
    ENTERPRISE = "enterprise"


async def run_full_pipeline(company_id: str, 
                            tier: PipelineTier = PipelineTier.CORE,
                            force_refresh: bool = False) -> Dict:
    """
    Orchestrates the entire data processing flow with resilience.
    
    Args:
        company_id: Company identifier
        tier: Algorithm tier (core or enterprise)
        force_refresh: If True, bypass cache and fetch fresh data
    
    Returns:
        Pipeline execution result with status and metrics
    """
    result = {
        "company_id": company_id,
        "tier": tier.value,
        "status": "started",
        "steps_completed": [],
        "errors": [],
        "metrics": {}
    }
    
    try:
        # 0. Check database health
        health = check_database_health()
        result["database_status"] = health["status"]
        
        if health["status"] == "unhealthy":
            result["status"] = "failed"
            result["errors"].append("Database completely unavailable")
            return result
        
        # 1. Get tokens
        tokens = get_company_tokens(company_id)
        result["steps_completed"].append("get_tokens")
        
        # 2. Sync data (Connectors) - only if online
        if health["supabase_available"]:
            print(f"[Pipeline] Syncing data for {company_id}...")
            
            if 'shopify' in tokens:
                try:
                    s = tokens['shopify']
                    sync_shopify(s['shop_url'], s['access_token'], company_id)
                    result["steps_completed"].append("sync_shopify")
                except Exception as e:
                    # Circuit breaker or sync error
                    result["errors"].append(f"Shopify sync: {e}")
            
            if 'meta' in tokens:
                try:
                    m = tokens['meta']
                    sync_meta_ads(m['account_id'], m['access_token'], company_id)
                    result["steps_completed"].append("sync_meta")
                except Exception as e:
                    result["errors"].append(f"Meta sync: {e}")

            if 'google' in tokens:
                try:
                    g = tokens['google']
                    from .connectors import sync_google_ads
                    sync_google_ads(g['customer_id'], g['access_token'], company_id)
                    result["steps_completed"].append("sync_google")
                except Exception as e:
                    result["errors"].append(f"Google sync: {e}")
            
            if 'klaviyo' in tokens:
                try:
                    k = tokens['klaviyo']
                    from .connectors import sync_klaviyo
                    sync_klaviyo(k['api_key'], company_id)
                    result["steps_completed"].append("sync_klaviyo")
                except Exception as e:
                    result["errors"].append(f"Klaviyo sync: {e}")

            if 'stripe' in tokens:
                try:
                    st = tokens['stripe']
                    from .connectors import sync_stripe
                    sync_stripe(st['api_key'], company_id)
                    result["steps_completed"].append("sync_stripe")
                except Exception as e:
                    result["errors"].append(f"Stripe sync: {e}")

            if 'ga4' in tokens:
                try:
                    g4 = tokens['ga4']
                    from .connectors import sync_ga4
                    sync_ga4(g4['property_id'], g4['credentials'], company_id)
                    result["steps_completed"].append("sync_ga4")
                except Exception as e:
                    result["errors"].append(f"GA4 sync: {e}")

            if 'gsc' in tokens:
                try:
                    gs = tokens['gsc']
                    from .connectors import sync_gsc
                    sync_gsc(gs['site_url'], gs['credentials'], company_id)
                    result["steps_completed"].append("sync_gsc")
                except Exception as e:
                    result["errors"].append(f"GSC sync: {e}")

        else:
            print(f"[Pipeline] Offline mode - using cached data for {company_id}")
            result["offline_mode"] = True
        
        # 3. Get data from DB (with cache fallback)
        df_ventas = get_ventas(company_id)
        
        if df_ventas.empty:
            result["status"] = "no_data"
            result["errors"].append("No sales data found")
            return result
        
        # 3.1 Data Guard (Sales)
        sales_errors = DataGuard.validate_sales_data(df_ventas)
        if sales_errors:
            result["status"] = "data_quality_error"
            result["errors"].extend([f"Sales Data: {e}" for e in sales_errors])
            # We halt execution if sales data is corrupt
            return result
        
        result["steps_completed"].append("get_ventas")
        result["metrics"]["sales_records"] = len(df_ventas)
        
        # 4. LTV & Churn Prediction
        predictions_result = await _run_predictions(
            company_id, df_ventas, tier, result
        )
        
        if predictions_result:
            result["metrics"]["customers_analyzed"] = len(predictions_result.get("predictions", []))
        
        # 5. Budget Optimization (if marketing data available)
        df_gastos = get_gastos(company_id)
        
        if not df_gastos.empty:
            # 5.1 Data Guard (Marketing)
            marketing_errors = DataGuard.validate_marketing_data(df_gastos)
            if marketing_errors:
                result["errors"].extend([f"Marketing Data: {e}" for e in marketing_errors])
                # We skip MMM but continue (partial success)
                result["steps_completed"].append("skip_mmm_data_error")
            else:
                await _run_optimization(company_id, df_gastos, tier, result)
        else:
            result["steps_completed"].append("skip_mmm_no_data")
        
        # 6. Process retry queue (background cleanup)
        process_retry_queue()
        
        result["status"] = "completed"
        print(f"[Pipeline] Pipeline complete for {company_id}")
        
    except Exception as e:
        result["status"] = "failed"
        result["errors"].append(str(e))
        print(f"[Pipeline] Error for {company_id}: {e}")
    
    return result


async def _run_predictions(company_id: str, df_ventas, 
                           tier: PipelineTier, result: Dict) -> Optional[Dict]:
    """
    Run LTV/Churn predictions using appropriate tier engine.
    """
    try:
        if tier == PipelineTier.ENTERPRISE:
            # Enterprise: LSTM-based predictions
            from core.engine_enterprise import run_enterprise_ltv_pipeline
            
            predictions = run_enterprise_ltv_pipeline(
                df_ventas,
                sequence_length=12,
                epochs=50
            )
            
            # Save with JSONB flexibility
            save_predictions(
                company_id=company_id,
                predictions=predictions["predictions"],
                model_type=predictions["model_type"],
                training_metrics=predictions["training_metrics"]
            )
            
            result["steps_completed"].append("predict_enterprise_lstm")
            
        else:
            # Core: BG/NBD + Gamma-Gamma
            engine = DataScienceCore()
            rfm = engine.prepare_data(df_ventas)
            core_predictions = engine.predict(rfm)
            final_segments = segment_customers(core_predictions)
            
            # Convert to list format for JSONB storage
            predictions_list = []
            for customer_id, row in final_segments.iterrows():
                predictions_list.append({
                    "customer_id": str(customer_id),
                    "ltv_predicted": float(row.get('clv_12m', 0)),
                    "churn_prob": float(1 - row.get('prob_alive', 0)),
                    "segment": row.get('segment', 'unknown')
                })
            
            predictions = {
                "predictions": predictions_list,
                "model_type": "BG_NBD_GammaGamma"
            }
            
            # Save with JSONB
            save_predictions(
                company_id=company_id,
                predictions=predictions_list,
                model_type="BG_NBD_GammaGamma"
            )
            
            result["steps_completed"].append("predict_core_bgnbd")
        
        return predictions
        
    except Exception as e:
        result["errors"].append(f"Predictions failed: {e}")
        return None


async def _run_optimization(company_id: str, df_gastos,
                            tier: PipelineTier, result: Dict) -> Optional[Dict]:
    """
    Run budget optimization using appropriate tier engine.
    """
    try:
        if tier == PipelineTier.ENTERPRISE:
            # Enterprise: Bayesian MMM with Nevergrad tuning
            from core.optimizer_enterprise import run_enterprise_mmm_pipeline
            import pandas as pd
            
            # Pivot gastos to channel columns
            spend_pivot = df_gastos.pivot_table(
                index='fecha', columns='canal', values='inversion',
                aggfunc='sum', fill_value=0
            )
            
            # Need revenue data - for now use a placeholder or derive from sales
            # In production, this would come from the join with sales data
            revenue_series = pd.Series([50000] * len(spend_pivot))  # Placeholder
            
            mmm_results = run_enterprise_mmm_pipeline(
                spend_df=spend_pivot,
                revenue_series=revenue_series,
                total_budget=spend_pivot.sum().sum() / len(spend_pivot)  # Average monthly
            )
            
            save_mmm_results(
                company_id=company_id,
                optimization_results=mmm_results,
                channel_posteriors=mmm_results.get("posterior_coefficients")
            )
            
            result["steps_completed"].append("optimize_enterprise_mmm")
            result["metrics"]["optimal_allocation"] = mmm_results.get("optimal_allocation")
            
        else:
            # Core: Simple optimization
            optimizer = BudgetOptimizer()
            
            # Group by channel
            channel_spend = df_gastos.groupby('canal')['inversion'].sum()
            channels = channel_spend.index.tolist()
            historical_spend = channel_spend.values
            
            total_budget = float(historical_spend.sum())
            
            # Simple optimization
            core_results = optimizer.optimize(
                total_budget=total_budget,
                channels=channels,
                historical_spend=historical_spend
            )
            
            save_insights_jsonb(
                company_id=company_id,
                insight_type="mmm_optimization",
                data=core_results,
                metadata={"tier": "core"}
            )
            
            result["steps_completed"].append("optimize_core")
        
        # 5.2 Enterprise Vault Backup (Model State)
        if tier == PipelineTier.ENTERPRISE:
            try:
                vault = SecureVault(company_id=company_id)
                # Store a snapshot of the current insight state as a 'model snapshot'
                vault.store_model_snapshot(
                    model_name="full_pipeline_state",
                    state=result["metrics"],
                    reason="scheduled"
                )
                result["steps_completed"].append("vault_model_snapshot")
            except Exception as ev:
                print(f"[Pipeline] Vault backup failed: {ev}")
                result["errors"].append(f"Vault backup failed: {ev}")

    except Exception as e:
        result["errors"].append(f"Optimization failed: {e}")
        return None


async def run_health_check() -> Dict:
    """
    Pipeline health check endpoint.
    """
    return check_database_health()


async def run_retry_processor():
    """
    Process pending retries (call periodically).
    """
    process_retry_queue()
    
    cache = get_local_cache()
    pending = cache.get_pending_retries()
    
    return {
        "processed": True,
        "pending_count": len(pending)
    }
