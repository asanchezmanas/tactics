import os
import pandas as pd
from typing import Optional, Dict, List, Any
from core.supabase_bridge import SupabaseBridge
from core.resilience import (
    with_fallback, decrypt_token, get_local_cache
)

# Initialize global SOTA bridge
db_bridge = SupabaseBridge()

def check_database_health() -> Dict:
    """Standardized health check using the bridge."""
    supabase_ok = db_bridge.client is not None
    cache = get_local_cache()
    
    local_ok = False
    try:
        cache.get("health_check")
        local_ok = True
    except Exception:
        local_ok = False
        
    status = "healthy" if supabase_ok and local_ok else "degraded" if local_ok else "unhealthy"
    
    return {
        "status": status,
        "supabase_available": supabase_ok,
        "local_cache_available": local_ok
    }

def process_retry_queue():
    """Proxy to local cache for recovery."""
    cache = get_local_cache()
    # Logic for background retry would go here
    pass

# ============================================================
# STANDARDIZED DATA ACCESS (W/ FALLBACK)
# ============================================================

@with_fallback(cache_key_fn=lambda company_id: f"ventas:{company_id}", ttl_hours=1)
def get_ventas(company_id: str) -> pd.DataFrame:
    """Fetches sales data from Supabase/Postgres."""
    data = db_bridge.get_company_data(company_id, "transactions")
    if not data:
        return pd.DataFrame()
    df = pd.DataFrame(data)
    # Ensure standard LTV columns
    if 'order_date' in df.columns:
        df['order_date'] = pd.to_datetime(df['order_date'])
    return df

@with_fallback(cache_key_fn=lambda company_id: f"gastos:{company_id}", ttl_hours=6)
def get_gastos(company_id: str) -> pd.DataFrame:
    """Fetches marketing spend data."""
    data = db_bridge.get_company_data(company_id, "marketing_spend")
    if not data:
        return pd.DataFrame()
    return pd.DataFrame(data)

@with_fallback(cache_key_fn=lambda company_id: f"tokens:{company_id}", ttl_hours=24)
def get_company_tokens(company_id: str) -> dict:
    """Retrieves and decrypts integration secrets."""
    # SOTA: This should ideally be moved to a more secure 'vault' integration
    if not db_bridge.client:
        return {}
    
    res = db_bridge.client.table("integrations").select("*").eq("company_id", company_id).execute()
    tokens = {item['service_name']: item for item in res.data}
    
    for service, data in tokens.items():
        if data.get('access_token'): data['access_token'] = decrypt_token(data['access_token'])
        if data.get('api_key'): data['api_key'] = decrypt_token(data['api_key'])
    return tokens

# ============================================================
# PERSISTENCE (VIA BRIDGE)
# ============================================================

def save_insights_jsonb(company_id: str, insight_type: str, data: Dict, metadata: Dict = None) -> bool:
    """Delegates persistence to the bridge."""
    return db_bridge.upsert_raw_payload(company_id, insight_type, [data])

def save_predictions(company_id: str, predictions: List[Dict], model_type: str, training_metrics: Dict = None) -> bool:
    data = {"predictions": predictions, "model_type": model_type, "generated_at": pd.Timestamp.now().isoformat()}
    return save_insights_jsonb(company_id, "customer_predictions", data, {"training_metrics": training_metrics})

def save_mmm_results(company_id: str, optimization_results: Dict, channel_posteriors: Dict = None) -> bool:
    return save_insights_jsonb(company_id, "mmm_optimization", optimization_results, {"posteriors": channel_posteriors})

def get_dashboard_metrics(company_id: str) -> dict:
    """Retrieves latest metrics from the hybrid layer."""
    if not db_bridge.client:
        return {"ltv_total": 0, "avg_churn": 0, "customer_count": 0}

    try:
        # SOTA: Query latest aggregated dashboard entry
        res = db_bridge.client.table("raw_payloads")\
            .select("payload")\
            .eq("company_id", company_id)\
            .eq("provider_id", "dashboard_metrics")\
            .order("ingested_at", descending=True)\
            .limit(1)\
            .execute()
        
        if res.data:
            return res.data[0]["payload"][0]
    except Exception as e:
        print(f"[DB] Dashboard fetch error: {e}")
    
    return {"ltv_total": 0, "avg_churn": 0, "customer_count": 0}

def get_high_risk_vips(company_id: str, limit: int = 5) -> list:
    """Fetches high-risk segments."""
    # Simplified lookup for full-stack integration
    return db_bridge.get_company_data(company_id, "sentiment_signals")[:limit]
