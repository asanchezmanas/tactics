import os
import pandas as pd
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None

def get_ventas(company_id: str) -> pd.DataFrame:
    """
    Fetches sales data for a specific company from Supabase.
    """
    if not supabase:
        return pd.DataFrame()
        
    response = supabase.table("ventas") \
        .select("cliente_id, fecha_venta, monto_total") \
        .eq("company_id", company_id) \
        .execute()
    
    if not response.data:
        return pd.DataFrame()
        
    df = pd.DataFrame(response.data)
    df.columns = ['customer_id', 'order_date', 'revenue']
    return df

def get_gastos(company_id: str) -> pd.DataFrame:
    """
    Fetches marketing expenses for a specific company.
    """
    if not supabase:
        return pd.DataFrame()
        
    response = supabase.table("gastos_marketing") \
        .select("fecha, canal, inversion, impresiones, clics") \
        .eq("company_id", company_id) \
        .execute()
        
    if not response.data:
        return pd.DataFrame()
        
    return pd.DataFrame(response.data)

def save_insights(company_id: str, df_insights: pd.DataFrame):
    """
    Saves or updates prediction results (LTV, Churn) in Supabase.
    """
    if not supabase or df_insights.empty:
        return

    # Prepare data for upsert
    # df_insights has customer_id as index
    data = []
    for customer_id, row in df_insights.iterrows():
        data.append({
            "company_id": company_id,
            "cliente_id": customer_id,
            "probabilidad_churn": 1 - row['prob_alive'],
            "ltv_predicho_12m": row['clv_12m'],
            "compras_esperadas_90d": row['expected_purchases_90d'],
            "ultima_actualizacion": pd.Timestamp.now().isoformat()
        })
    
    # Batch upsert
    supabase.table("insights_core").upsert(data).execute()

def get_company_tokens(company_id: str) -> dict:
    """
    Retrieves integration tokens for a company.
    """
    if not supabase:
        return {}
        
    response = supabase.table("integrations") \
        .select("service_name, access_token, shop_url") \
        .eq("company_id", company_id) \
        .execute()
        
    return {item['service_name']: item for item in response.data}

def get_dashboard_metrics(company_id: str):
    """
    Fetches aggregate metrics for the dashboard.
    """
    if not supabase:
        return {"ltv_total": 0, "avg_churn": 0, "customer_count": 0}

    # Prediction Aggregates
    res_insights = supabase.table("insights_core") \
        .select("ltv_predicho_12m, probabilidad_churn") \
        .eq("company_id", company_id) \
        .execute()
    
    df = pd.DataFrame(res_insights.data)
    if df.empty:
        return {"ltv_total": 0, "avg_churn": 0, "customer_count": 0}
        
    return {
        "ltv_total": float(df['ltv_predicho_12m'].sum()),
        "avg_churn": float(df['probabilidad_churn'].mean()),
        "customer_count": len(df)
    }

def get_high_risk_vips(company_id: str, limit: int = 5):
    """
    Fetches customers with high LTV but high churn risk.
    """
    if not supabase:
        return []

    res = supabase.table("insights_core") \
        .select("probabilidad_churn, ltv_predicho_12m, clientes(nombre, email)") \
        .eq("company_id", company_id) \
        .order("ltv_predicho_12m", desc=True) \
        .limit(limit) \
        .execute()
    
    return res.data
