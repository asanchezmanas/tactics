import os
import pandas as pd
from dotenv import load_dotenv
from supabase import create_client, Client
from typing import Optional, Dict, List, Any
from core.resilience import (
    with_fallback, with_retry_queue, get_local_cache,
    encrypt_token, decrypt_token, LocalCache
)

load_dotenv()

# ============================================================
# SUPABASE CLIENT
# ============================================================

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Optional[Client] = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None

def check_database_health() -> Dict:
    """Check database connectivity and cache status."""
    cache = get_local_cache()
    try:
        supabase_ok = False
        if supabase:
            res = supabase.table("companies").select("count", count="exact").limit(1).execute()
            supabase_ok = True
    except Exception:
        supabase_ok = False
        
    local_ok = False
    try:
        cache.get("health_check")
        local_ok = True
    except Exception:
        local_ok = False
        
    status = "healthy" if supabase_ok and local_ok else "degraded" if local_ok else "unhealthy"
    
    pending_count = 0
    if local_ok:
        try:
            pending_count = len(cache.get_pending_retries())
        except Exception: pass

    return {
        "status": status,
        "supabase_available": supabase_ok,
        "local_cache_available": local_ok,
        "pending_retries": pending_count
    }

def process_retry_queue():
    """Process pending retries (proxy to local cache)."""
    # In a real app, this would iterate through the retry_queue and re-attempt writes
    print("[DB] Processing retry queue (stub)")
    pass

# ============================================================
# RESILIENT DATA ACCESS FUNCTIONS
# ============================================================

@with_fallback(cache_key_fn=lambda company_id: f"ventas:{company_id}", ttl_hours=1)
def get_ventas(company_id: str) -> pd.DataFrame:
    if not supabase: raise ConnectionError("Supabase not configured")
    res = supabase.table("ventas").select("cliente_id, fecha_venta, monto_total").eq("company_id", company_id).execute()
    if not res.data: return pd.DataFrame()
    df = pd.DataFrame(res.data)
    df.columns = ['customer_id', 'order_date', 'revenue']
    return df

@with_fallback(cache_key_fn=lambda company_id: f"gastos:{company_id}", ttl_hours=6)
def get_gastos(company_id: str) -> pd.DataFrame:
    if not supabase: raise ConnectionError("Supabase not configured")
    res = supabase.table("gastos_marketing").select("fecha, canal, inversion, impresiones, clics").eq("company_id", company_id).execute()
    if not res.data: return pd.DataFrame()
    return pd.DataFrame(res.data)

@with_fallback(cache_key_fn=lambda company_id: f"tokens:{company_id}", ttl_hours=24)
def get_company_tokens(company_id: str) -> dict:
    if not supabase: raise ConnectionError("Supabase not configured")
    res = supabase.table("integrations").select("service_name, account_id, access_token, api_key, shop_url, credentials").eq("company_id", company_id).execute()
    tokens = {item['service_name']: item for item in res.data}
    for service, data in tokens.items():
        if data.get('access_token'): data['access_token'] = decrypt_token(data['access_token'])
        if data.get('api_key'): data['api_key'] = decrypt_token(data['api_key'])
    return tokens

# ============================================================
# RESILIENT WRITE FUNCTIONS
# ============================================================

# Note: with_retry_queue from core.resilience is a stub for now, 
# but we apply it to follow the pattern.

def save_insights_jsonb(company_id: str, insight_type: str, data: Dict, metadata: Dict = None) -> bool:
    if not supabase: return False
    payload = {
        "company_id": company_id,
        "insight_type": insight_type,
        "data": data,
        "metadata": metadata or {},
        "created_at": pd.Timestamp.now().isoformat()
    }
    try:
        supabase.table("insights_jsonb").insert(payload).execute()
        return True
    except Exception:
        # Fallback to local cache for persistence
        get_local_cache().set(f"insight:{company_id}:{insight_type}", payload, "insights_jsonb")
        return False

def save_predictions(company_id: str, predictions: List[Dict], model_type: str, training_metrics: Dict = None) -> bool:
    data = {"predictions": predictions, "model_type": model_type, "generated_at": pd.Timestamp.now().isoformat()}
    return save_insights_jsonb(company_id, "customer_predictions", data, {"training_metrics": training_metrics})

def save_mmm_results(company_id: str, optimization_results: Dict, channel_posteriors: Dict = None) -> bool:
    return save_insights_jsonb(company_id, "mmm_optimization", optimization_results, {"posteriors": channel_posteriors})

def get_dashboard_metrics(company_id: str) -> dict:
    # Attempt to get from JSONB first (more flexible)
    try:
        res = supabase.table("insights_jsonb").select("data").eq("company_id", company_id).eq("insight_type", "dashboard_metrics").order("created_at", desc=True).limit(1).execute()
        if res.data: return res.data[0]['data']
    except Exception: pass
    
    # Fallback to legacy structure or cache
    return {"ltv_total": 0, "avg_churn": 0, "customer_count": 0}

def get_high_risk_vips(company_id: str, limit: int = 5) -> list:
    if not supabase: return []
    res = supabase.table("insights_core").select("probabilidad_churn, ltv_predicho_12m, clientes(nombre, email)").eq("company_id", company_id).order("ltv_predicho_12m", desc=True).limit(limit).execute()
    return res.data
