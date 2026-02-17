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
from core.engine import DataScienceCore

logger = logging.getLogger("tactics.pipeline")

class PipelineTier(str, Enum):
    CORE = "core"
    ENTERPRISE = "enterprise"

async def run_full_pipeline(company_id: str, 
                            tier: PipelineTier = PipelineTier.CORE,
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
                await _run_optimization(company_id, df_gastos, tier, result)
        
        # 6. Cleanup
        process_retry_queue()
        result["status"] = "completed"
        
    except Exception as e:
        result["status"] = "failed"
        result["errors"].append(str(e))
        logger.error(f"Pipeline error for {company_id}: {e}")
    
    return result

async def _run_predictions(company_id: str, df_ventas, tier: PipelineTier, result: Dict):
    """BG/NBD + Gamma-Gamma Prediction Core."""
    try:
        engine = DataScienceCore()
        rfm = engine.prepare_data(df_ventas)
        core_predictions = engine.predict(rfm)
        final_segments = segment_customers(core_predictions)
        
        predictions_list = []
        for customer_id, row in final_segments.iterrows():
            predictions_list.append({
                "customer_id": str(customer_id),
                "ltv_predicted": float(row.get('clv_12m', 0)),
                "churn_prob": float(1 - row.get('prob_alive', 0)),
                "segment": row.get('segment', 'unknown')
            })
        
        save_predictions(company_id, predictions_list, "BG_NBD_GammaGamma")
        result["steps_completed"].append("predict_ltv")
        result["metrics"]["customers_analyzed"] = len(predictions_list)
    except Exception as e:
        result["errors"].append(f"Predictions failed: {e}")

async def _run_optimization(company_id: str, df_gastos, tier: PipelineTier, result: Dict):
    """MMM Optimization Core."""
    try:
        optimizer = BudgetOptimizer()
        channel_spend = df_gastos.groupby('canal')['inversion'].sum()
        core_results = optimizer.optimize(
            total_budget=float(channel_spend.sum()),
            channels=channel_spend.index.tolist(),
            historical_spend=channel_spend.values
        )
        save_mmm_results(company_id, core_results)
        result["steps_completed"].append("optimize_mmm")
    except Exception as e:
        result["errors"].append(f"Optimization failed: {e}")
