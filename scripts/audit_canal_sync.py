"""
Audit Script: Data Consistency & Canal Sync
Analyzes discrepancies between 'ventas' (sales) and 'gastos_marketing' (marketing) channel names.
"""

import os
import pandas as pd
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

def run_audit(company_id: str):
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    if not url or not key:
        print("❌ Supabase credentials missing.")
        return

    supabase: Client = create_client(url, key)

    print(f"--- Auditing Company: {company_id} ---")

    # 1. Fetch Sales Channels
    res_sales = supabase.table("ventas")\
        .select("canal")\
        .eq("company_id", company_id)\
        .execute()
    
    sales_channels = set(pd.DataFrame(res_sales.data)['canal'].unique()) if res_sales.data else set()
    print(f"Sales Channels found: {sales_channels}")

    # 2. Fetch Marketing Channels
    res_mkt = supabase.table("gastos_marketing")\
        .select("canal")\
        .eq("company_id", company_id)\
        .execute()
    
    mkt_channels = set(pd.DataFrame(res_mkt.data)['canal'].unique()) if res_mkt.data else set()
    print(f"Marketing Channels found: {mkt_channels}")

    # 3. Analyze Discrepancies
    unmatched_sales = sales_channels - mkt_channels
    unmatched_mkt = mkt_channels - sales_channels

    print("\n--- Summary ---")
    if unmatched_sales:
        print(f"⚠️ Sales channels with NO matching marketing data: {unmatched_sales}")
        print("   (These might be organic, direct, or misnamed)")
    
    if unmatched_mkt:
        print(f"⚠️ Marketing channels with NO matching sales data: {unmatched_mkt}")
        print("   (Possible naming mismatch: e.g. 'FB' vs 'Facebook')")

    if not unmatched_sales and not unmatched_mkt:
        print("✅ Channels perfectly aligned!")
    
    # 4. Data Quality Check: Nulls
    res_nulls = supabase.table("ventas")\
        .select("id")\
        .eq("company_id", company_id)\
        .is_("canal", "null")\
        .execute()
    
    null_count = len(res_nulls.data) if res_nulls.data else 0
    if null_count > 0:
        print(f"🚨 Sales records with NULL canal: {null_count}")

if __name__ == "__main__":
    # Using a typical demo company_id if not provided
    run_audit("demo_company")
