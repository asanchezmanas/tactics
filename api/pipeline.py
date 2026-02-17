"""
Resilient Data Pipeline for Tactics (v3.0 - SOTA Async)
Orchestrates the 'Golden Triangle': Spend (Ads), Revenue (Sales), and Sentiment (Support).
"""

import os
import json
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Optional, Dict, List
from enum import Enum
import pandas as pd

# Standardized database layer
from .database import (
    get_ventas, get_gastos, get_company_tokens,
    save_insights_jsonb, save_predictions, save_mmm_results,
    check_database_health, process_retry_queue
)

# Connectors (Unified Async Hub)
from connectors.sync import UnifiedSyncHub

# Core algorithms
from core.segmentation import segment_customers
from core.optimizer import BudgetOptimizer
from core.resilience import DataGuard
from core.engine import TacticalEngine
from core.metrics_factory import BusinessMetricsFactory

logger = logging.getLogger("tactics.pipeline")

class PipelineTier(str, Enum):
    INTELLIGENCE = "intelligence"
    OPTIMISATION = "optimisation"
    PRECISION = "precision"

async def run_full_pipeline(company_id: str, 
                            tier: PipelineTier = PipelineTier.INTELLIGENCE,
                            force_refresh: bool = False) -> Dict:
    """
    Orchestrates the entire data processing flow using SOTA Async Hub.
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
        
        # 1. Get credentials/tokens
        tokens = get_company_tokens(company_id)
        result["steps_completed"].append("get_tokens")
        
        # 2. Universal Async Ingestion (Golden Triangle)
        if health["supabase_available"] and tokens:
            logger.info(f"SOTA Async Sync starting for {company_id}...")
            hub = UnifiedSyncHub()
            sync_results = await hub.sync_company(company_id, tokens)
            
            from api.data_ingestion import DataIngestion
            ingestion = DataIngestion(company_id)
            for provider_id, sync_res in sync_results.items():
                if isinstance(sync_res, dict) and sync_res.get("status") == "success":
                    data = sync_res.get("data", [])
                    if data:
                        dtype = "ventas" if provider_id == 'shopify' else "gastos"
                        ingestion.ingest_json(data, dtype)
            
            for provider, res in sync_results.items():
                if isinstance(res, dict) and res.get("status") == "success":
                    result["steps_completed"].append(f"sync_{provider}")
                elif isinstance(res, Exception):
                    result["errors"].append(f"{provider} sync error: {str(res)}")
                else:
                    result["errors"].append(f"{provider} sync failed: {res}")
        else:
            logger.warning(f"Offline mode or no tokens - using cache for {company_id}")
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
            return result
        
        result["steps_completed"].append("get_ventas")
        result["metrics"]["sales_records"] = len(df_ventas)
        
        # 4. LTV & Churn Prediction
        await _run_predictions(company_id, df_ventas, tier, result)
        
        # 5. Budget Optimization
        df_gastos = get_gastos(company_id)
        if not df_gastos.empty:
            marketing_errors = DataGuard.validate_marketing_data(df_gastos)
            if not marketing_errors:
                await _run_optimization(company_id, df_gastos, tier, result, df_ventas=df_ventas)
        
        # 6. Dashboard Aggregation (High-level synthesis for UI)
        await _generate_dashboard_summary(company_id, result)
        
        # 7. Cleanup
        process_retry_queue()
        result["status"] = "completed"
        
    except Exception as e:
        result["status"] = "failed"
        result["errors"].append(str(e))
        logger.error(f"Pipeline error for {company_id}: {e}")
    
    return result

async def _run_predictions(company_id: str, df_ventas, tier: PipelineTier, result: Dict):
    """Tier-aware LTV/Churn prediction."""
    try:
        engine = TacticalEngine(tier=tier.value, company_id=company_id)
        prediction_results = engine.analyze_ltv(df_ventas)
        
        result["metrics"]["avg_ltv"] = prediction_results['summary'].get('avg_ltv', 0)
        result["metrics"]["avg_churn"] = prediction_results['summary'].get('avg_churn_risk', 0)
        
        save_predictions(company_id, prediction_results['predictions'], "TacticalEngine")
        
        result["steps_completed"].append("predict_ltv")
        result["metrics"]["customers_analyzed"] = prediction_results['summary'].get('customers_analyzed', len(prediction_results['predictions']))
    except Exception as e:
        result["errors"].append(f"Predictions failed: {e}")

async def _run_optimization(company_id: str, df_gastos, tier: PipelineTier, result: Dict, df_ventas = None):
    """MMM Optimization Core with LTV weighting."""
    try:
        # 1. Calculate Business Metrics & Optimizer Priors
        factory = BusinessMetricsFactory(company_id)
        report = factory.calculate_all(df_ventas if df_ventas is not None else pd.DataFrame(), df_gastos)
        priors = report.synthesis.get("optimizer_priors", {})
        
        # 2. Run Optimization
        optimizer = BudgetOptimizer()
        channel_spend = df_gastos.groupby('channel')['spend'].sum()
        
        # Prepare channel params including priors
        channels = channel_spend.index.tolist()
        channel_params = {}
        for c in channels:
            # Shift amplitude based on LTV prior (Weighted ROAS)
            prior = priors.get(c, 1.0)
            channel_params[c] = {
                "amplitude": 10000 * prior, # Scaled by LTV prior
                "alpha": 1.2,               # Shape
                "gamma": 800.0,             # Half-saturation point
                "margin": 0.4               # Default margin
            }

        core_results = optimizer.allocate_budget(
            total_budget=float(channel_spend.sum()),
            channels=channels,
            channel_params=channel_params
        )
        
        save_mmm_results(company_id, core_results)
        result["steps_completed"].append("optimize_mmm")
        
        # Calculate real MAPE if we have sales data
        revenue_series = pd.Series()
        if df_ventas is not None and not df_ventas.empty:
            # Resample to weekly revenue for MMM
            df_ventas['order_date'] = pd.to_datetime(df_ventas['order_date'])
            revenue_series = df_ventas.set_index('order_date')['revenue'].resample('W').sum()
            
        if not df_gastos.empty:
            df_gastos['date'] = pd.to_datetime(df_gastos['date'])
            spend_series = df_gastos.pivot_table(index='date', columns='channel', values='spend', aggfunc='sum').resample('W').sum().fillna(0)

        result["metrics"]["mmm_mape"] = optimizer.validate_holdout(spend_series, revenue_series)
    except Exception as e:
        result["errors"].append(f"Optimization failed: {e}")
        logger.error(f"Optimization error: {e}")

async def _generate_dashboard_summary(company_id: str, pipeline_result: Dict):
    """Aggregates all steps into a single dashboard_metrics entry for fast UI load."""
    metrics = pipeline_result.get("metrics", {})
    
    summary = {
        "ltv_total": metrics.get("avg_ltv", 0) * metrics.get("customers_analyzed", 0),
        "avg_churn": metrics.get("avg_churn", 0.12),
        "customer_count": metrics.get("sales_records", 0),
        "last_sync": datetime.now().isoformat(),
        "performance_signals": {
            "mmm_trust": 1.0 - metrics.get("mmm_mape", 0.15),
            "data_quality": 1.0 if not pipeline_result.get("errors") else 0.7
        }
    }
    
    from api.database import save_insights_jsonb
    save_insights_jsonb(company_id, "dashboard_metrics", summary)
