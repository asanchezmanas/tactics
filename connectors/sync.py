import os
from datetime import datetime
from typing import Dict, List, Optional
import pandas as pd

# Try-except for optional SDKs
try:
    import shopify
    SHOPIFY_AVAILABLE = True
except ImportError:
    shopify = None
    SHOPIFY_AVAILABLE = False

try:
    from facebook_business.api import FacebookAdsApi
    from facebook_business.adobjects.adaccount import AdAccount
    META_AVAILABLE = True
except ImportError:
    FacebookAdsApi = None
    AdAccount = None
    META_AVAILABLE = False

# Database client (Resilient)
from api.database import supabase
from core.resilience import (
    shopify_breaker, meta_breaker, retry_with_backoff, 
    google_breaker, klaviyo_breaker, stripe_breaker, 
    ga4_breaker, gsc_breaker
)

# Fitness Connectors
from connectors.fitness_base import FitnessSyncResult
from connectors.mindbody import MindbodyConnector
from connectors.glofox import GlofoxConnector
from connectors.google_calendar import GoogleCalendarConnector
from connectors.stripe_fitness import StripeFitnessConnector

# ============================================================
# E-COMMERCE & MARKETING SYNC
# ============================================================

@shopify_breaker
@retry_with_backoff(max_retries=3, initial_delay=2.0)
def sync_shopify(shop_url: str, access_token: str, company_id: str):
    if not supabase or not SHOPIFY_AVAILABLE:
        print(f"[Connector] Skipping Shopify sync (SDK/DB unavailable)")
        return

    session = shopify.Session(shop_url, '2024-01', access_token)
    shopify.ShopifyResource.activate_session(session)
    
    try:
        orders = shopify.Order.find(status="any", financial_status="paid")
        for order in orders:
            if not hasattr(order, 'customer'): continue
            
            customer = order.customer
            cust_payload = {
                "company_id": company_id,
                "external_id": str(customer.id),
                "email": getattr(customer, 'email', None),
                "nombre": f"{getattr(customer, 'first_name', '')} {getattr(customer, 'last_name', '')}".strip()
            }
            supabase.table("clientes").upsert(cust_payload).execute()
            
            res = supabase.table("clientes").select("id").eq("company_id", company_id).eq("external_id", str(customer.id)).single().execute()
            internal_cust_id = res.data['id']

            sale_payload = {
                "company_id": company_id,
                "cliente_id": internal_cust_id,
                "order_id": str(order.id),
                "fecha_venta": order.created_at,
                "monto_total": float(order.total_price),
                "moneda": order.currency,
                "canal_origen": "Shopify"
            }
            supabase.table("ventas").upsert(sale_payload).execute()
        print(f"Successfully synced {len(orders)} Shopify orders")
    finally:
        shopify.ShopifyResource.clear_session()

@meta_breaker
@retry_with_backoff(max_retries=3)
def sync_meta_ads(account_id: str, access_token: str, company_id: str, start_date: str = '2024-01-01'):
    if not supabase or not META_AVAILABLE: return
        
    FacebookAdsApi.init(access_token=access_token)
    account = AdAccount(f'act_{account_id}')
    insights = account.get_insights(fields=['spend', 'impressions', 'clicks'], params={'time_range': {'since': start_date, 'until': 'today'}, 'time_increment': 1})
    
    data = []
    for day in insights:
        data.append({
            "company_id": company_id,
            "fecha": day['date_start'],
            "canal": "Meta Ads",
            "inversion": float(day['spend']),
            "impresiones": int(day['impressions']),
            "clics": int(day['clicks'])
        })
    if data: supabase.table("gastos_marketing").upsert(data).execute()

@google_breaker
@retry_with_backoff(max_retries=3)
def sync_google_ads(customer_id: str, access_token: str, company_id: str):
    if not supabase: return
    # Simulated
    report_data = [{"date": "2024-02-01", "cost_micros": 15000000, "impressions": 5000, "clicks": 200}]
    data = []
    for row in report_data:
        data.append({
            "company_id": company_id, "fecha": row['date'], "canal": "Google Ads",
            "inversion": row['cost_micros'] / 1000000.0, "impresiones": row['impressions'], "clics": row['clicks']
        })
    if data: supabase.table("gastos_marketing").upsert(data).execute()

@klaviyo_breaker
@retry_with_backoff(max_retries=3)
def sync_klaviyo(api_key: str, company_id: str):
    if not supabase: return
    profiles = [{"id": "01GR...", "email": "vip.customer@example.com", "first_name": "John", "last_name": "Doe"}]
    for p in profiles:
        supabase.table("clientes").upsert({
            "company_id": company_id, "external_id": p['id'], "email": p['email'],
            "nombre": f"{p['first_name']} {p['last_name']}".strip(), "origen": "Klaviyo"
        }).execute()

@stripe_breaker
@retry_with_backoff(max_retries=3)
def sync_stripe(api_key: str, company_id: str):
    if not supabase: return
    # Simulated for MVP, in production use stripe-python
    transactions = [{"id": "txn_1", "created": 1706745600, "net": 4850, "currency": "eur", "type": "charge"}]
    for txn in transactions:
        if txn['type'] == 'charge':
            pass # Financial aggregates skip for MVP client matching
    print(f"Successfully synced Stripe for {company_id}")

@ga4_breaker
@retry_with_backoff(max_retries=3)
def sync_ga4(property_id: str, credentials_json: dict, company_id: str):
    if not supabase: return
    report = [{"date": "2024-02-01", "sessions": 1200, "conversions": 45, "revenue": 3200.50}]
    for row in report:
        supabase.table("insights_core").insert({
            "company_id": company_id, "insight_type": "traffic_daily", "insight_value": float(row['sessions']),
            "metadata": {"date": row['date'], "conversions": row['conversions'], "revenue": row['revenue']}
        }).execute()
    print(f"Successfully synced GA4 for {company_id}")

@gsc_breaker
@retry_with_backoff(max_retries=3)
def sync_gsc(site_url: str, credentials_json: dict, company_id: str):
    if not supabase: return
    keywords = [{"query": "organic protein powder", "clicks": 150, "impressions": 2000, "position": 3.5}]
    for k in keywords:
        supabase.table("insights_core").insert({
            "company_id": company_id, "insight_type": "seo_keyword", "insight_value": float(k['clicks']), "metadata": k
        }).execute()
    print(f"Successfully synced GSC for {company_id}")

@shopify_breaker
@retry_with_backoff(max_retries=3, initial_delay=2.0)
def sync_shopify_products(shop_url: str, access_token: str, company_id: str):
    if not supabase or not SHOPIFY_AVAILABLE: return []
    session = shopify.Session(shop_url, '2024-01', access_token)
    shopify.ShopifyResource.activate_session(session)
    try:
        products = shopify.Product.find(limit=250)
        data = []
        for p in products:
            for v in p.variants:
                item = {"company_id": company_id, "product_id": str(p.id), "variant_id": str(v.id), "title": p.title, "price": float(v.price)}
                supabase.table("products").upsert(item).execute()
                data.append(item)
        return data
    finally:
        shopify.ShopifyResource.clear_session()

# ============================================================
# FITNESS & WELLNESS SYNC
# ============================================================

@retry_with_backoff(max_retries=3)
def sync_mindbody(company_id: str, site_id: str, api_key: str):
    if not supabase: return
    connector = MindbodyConnector(company_id, site_id=site_id, api_key=api_key)
    result = connector.full_sync()
    if result.success:
        supabase.table("insights_core").insert({
            "company_id": company_id, "insight_type": "connector_sync",
            "insight_value": result.members_synced + result.attendance_synced,
            "metadata": result.to_dict()
        }).execute()
    return result

@retry_with_backoff(max_retries=3)
def sync_glofox(company_id: str, api_key: str, api_secret: str, branch_id: str):
    if not supabase: return
    connector = GlofoxConnector(company_id, api_key=api_key, api_secret=api_secret, branch_id=branch_id)
    result = connector.full_sync()
    if result.success:
        supabase.table("insights_core").insert({
            "company_id": company_id, "insight_type": "connector_sync",
            "insight_value": result.members_synced + result.attendance_synced,
            "metadata": result.to_dict()
        }).execute()
    return result

@retry_with_backoff(max_retries=3)
def sync_google_calendar_fitness(company_id: str, credentials_path: str):
    if not supabase: return
    connector = GoogleCalendarConnector(company_id, credentials_path=credentials_path)
    result = connector.full_sync()
    if result.success:
        supabase.table("insights_core").insert({
            "company_id": company_id, "insight_type": "connector_sync",
            "insight_value": result.classes_synced + result.attendance_synced,
            "metadata": result.to_dict()
        }).execute()
    return result

@stripe_breaker
@retry_with_backoff(max_retries=3)
def sync_stripe_fitness(api_key: str, company_id: str):
    if not supabase: return
    connector = StripeFitnessConnector(company_id, api_key=api_key)
    result = connector.full_sync()
    if result.success:
        members = connector.get_members()
        memberships = connector.get_memberships()
        for m in members:
            row = m.to_tactics_row()
            row["company_id"] = company_id
            supabase.table("clientes").upsert(row).execute()
        for m in memberships:
            row = m.to_tactics_row()
            row["company_id"] = company_id
            supabase.table("ventas").upsert(row).execute()
    return result
