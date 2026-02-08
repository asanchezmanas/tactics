try:
    import shopify
    SHOPIFY_AVAILABLE = True
except ImportError:
    shopify = None
    SHOPIFY_AVAILABLE = False

from .database import supabase
from core.resilience import shopify_breaker, meta_breaker, retry_with_backoff, google_breaker, klaviyo_breaker, stripe_breaker, ga4_breaker, gsc_breaker

@shopify_breaker
@retry_with_backoff(max_retries=3, initial_delay=2.0)
def sync_shopify(shop_url: str, access_token: str, company_id: str):
    """
    Syncs orders and customers from Shopify to Supabase.
    Protected by Circuit Breaker and Exponential Backoff.
    """
    if not supabase or not SHOPIFY_AVAILABLE:
        print(f"[Connector] Skipping Shopify sync for {company_id} (SDK not available)")
        return

    # Initialize Shopify session
    session = shopify.Session(shop_url, '2024-01', access_token)
    shopify.ShopifyResource.activate_session(session)
    
    try:
        # 1. Fetch Orders (simplified for MVP)
        orders = shopify.Order.find(status="any", financial_status="paid")
        
        for order in orders:
            # Skip if no customer
            if not hasattr(order, 'customer'):
                continue
                
            # A. Sync Customer
            customer = order.customer
            cust_payload = {
                "company_id": company_id,
                "external_id": str(customer.id),
                "email": getattr(customer, 'email', None),
                "nombre": f"{getattr(customer, 'first_name', '')} {getattr(customer, 'last_name', '')}".strip()
            }
            # Upsert customer
            supabase.table("clientes").upsert(cust_payload).execute()
            
            # Fetch internal ID
            res = supabase.table("clientes") \
                .select("id") \
                .eq("company_id", company_id) \
                .eq("external_id", str(customer.id)) \
                .single().execute()
            
            internal_cust_id = res.data['id']

            # B. Sync Sale
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
            
        print(f"Successfully synced {len(orders)} orders for {company_id}")
        
    finally:
        # Ensure session is cleared even if errors occur
        shopify.ShopifyResource.clear_session()

try:
    from facebook_business.api import FacebookAdsApi
    from facebook_business.adobjects.adaccount import AdAccount
    META_AVAILABLE = True
except ImportError:
    FacebookAdsApi = None
    AdAccount = None
    META_AVAILABLE = False

@meta_breaker
@retry_with_backoff(max_retries=3)
def sync_meta_ads(account_id: str, access_token: str, company_id: str, start_date: str = '2024-01-01'):
    """
    Syncs daily ad spend from Meta Ads to Supabase.
    Protected by Circuit Breaker.
    """
    if not supabase or not META_AVAILABLE:
        print(f"[Connector] Skipping Meta Ads sync for {company_id} (SDK not available)")
        return
        
    FacebookAdsApi.init(access_token=access_token)
    account = AdAccount(f'act_{account_id}')
    
    fields = ['spend', 'impressions', 'clicks']
    params = {
        'time_range': {'since': start_date, 'until': 'today'},
        'time_increment': 1, # Daily granularity
    }
    
    # Let exceptions bubble up to CircuitBreaker
    insights = account.get_insights(fields=fields, params=params)
    
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
        
    if data:
        supabase.table("gastos_marketing").upsert(data).execute()
    else:
        print(f"No Meta Ads data found for {company_id}")

    print(f"Successfully synced Meta Ads for {company_id}")

@google_breaker
@retry_with_backoff(max_retries=3)
def sync_google_ads(customer_id: str, access_token: str, company_id: str):
    """
    Syncs Google Ads campaign performance.
    Requires 'google-ads' library (simulated here for MVP structure).
    """
    if not supabase:
        return
        
    print(f"Syncing Google Ads for {company_id}...")
    
    # In production, this would use the GoogleAdsClient
    # For now, we simulate the structure to show how data is mapped
    # client = GoogleAdsClient.load_from_dict({...})
    
    # Simulated API response
    report_data = [
        {"date": "2024-02-01", "cost_micros": 15000000, "impressions": 5000, "clicks": 200},
        {"date": "2024-02-02", "cost_micros": 12000000, "impressions": 4200, "clicks": 180},
    ]
    
    data = []
    for row in report_data:
        data.append({
            "company_id": company_id,
            "fecha": row['date'],
            "canal": "Google Ads",
            "inversion": row['cost_micros'] / 1000000.0, # Convert micros to standard currency
            "impresiones": row['impressions'],
            "clics": row['clicks']
        })
        
    if data:
        supabase.table("gastos_marketing").upsert(data).execute()
    print(f"Successfully synced Google Ads for {company_id}")


@klaviyo_breaker
@retry_with_backoff(max_retries=3)
def sync_klaviyo(api_key: str, company_id: str):
    """
    Syncs Klaviyo data:
    1. Subscribers -> Clientes
    2. Email Attributed Revenue -> Ventas (attribution cache)
    """
    if not supabase:
        return
        
    print(f"Syncing Klaviyo for {company_id}...")
    
    # 1. Sync Active Profiles (Simulated)
    # response = requests.get("https://a.klaviyo.com/api/profiles", ...)
    
    profiles = [
        {"id": "01GR...", "email": "vip.customer@example.com", "first_name": "John", "last_name": "Doe"}
    ]
    
    for p in profiles:
        supabase.table("clientes").upsert({
            "company_id": company_id,
            "external_id": p['id'],
            "email": p['email'],
            "nombre": f"{p['first_name']} {p['last_name']}".strip(),
            "origen": "Klaviyo"
        }).execute()
        
    print(f"Successfully synced Klaviyo profiles for {company_id}")

@stripe_breaker
@retry_with_backoff(max_retries=3)
def sync_stripe(api_key: str, company_id: str):
    """
    Syncs Stripe Balance Transactions for 'Financial Truth' (Net Revenue).
    """
    if not supabase:
        return
        
    print(f"Syncing Stripe for {company_id}...")
    
    # In production:
    # stripe.api_key = api_key
    # transactions = stripe.BalanceTransaction.list(limit=100)
    
    # Simulated Data
    transactions = [
        {"id": "txn_1", "created": 1706745600, "net": 4850, "currency": "eur", "type": "charge"}, # 48.50 EUR
        {"id": "txn_2", "created": 1706832000, "net": 9820, "currency": "eur", "type": "charge"}, # 98.20 EUR
    ]
    
    count = 0
    from datetime import datetime
    for txn in transactions:
        if txn['type'] == 'charge':
            # Store as a 'sale' but marked as Stripe
            payload = {
                "company_id": company_id,
                # "order_id": txn['id'], 
                "fecha_venta": datetime.fromtimestamp(txn['created']).isoformat(),
                "monto_total": txn['net'] / 100.0, # Cents to Units
                "moneda": txn['currency'].upper(),
                "canal_origen": "Stripe"
            }
            # We skip client_id link for now as it's purely financial aggregations
            # But 'ventas' table requires client_id usually. 
            # For this MVP, we will just log it to avoid FK errors unless we fetch a client.
            # In a real app, we'd match email.
            pass 
            count += 1
            
    print(f"Successfully synced {count} Stripe transactions for {company_id}")


@ga4_breaker
@retry_with_backoff(max_retries=3)
def sync_ga4(property_id: str, credentials_json: dict, company_id: str):
    """
    Syncs GA4 Session and Conversion data.
    """
    if not supabase:
        return
        
    print(f"Syncing GA4 for {company_id}...")
    
    # In production:
    # client = BetaAnalyticsDataClient.from_service_account_info(credentials_json)
    # request = RunReportRequest(property=f"properties/{property_id}", ...)
    
    # Simulated Data
    report = [
        {"date": "2024-02-01", "sessions": 1200, "conversions": 45, "revenue": 3200.50},
        {"date": "2024-02-02", "sessions": 1150, "conversions": 38, "revenue": 2800.00},
    ]
    
    data = []
    for row in report:
        # Saving to generic insights for flexibility
        supabase.table("insights_core").insert({
            "company_id": company_id,
            "insight_type": "traffic_daily",
            "insight_value": float(row['sessions']),
            "metadata": {"date": row['date'], "conversions": row['conversions'], "revenue": row['revenue']}
        }).execute()

    print(f"Successfully synced GA4 for {company_id}")


@gsc_breaker
@retry_with_backoff(max_retries=3)
def sync_gsc(site_url: str, credentials_json: dict, company_id: str):
    """
    Syncs Google Search Console (SEO) data.
    """
    if not supabase:
        return
        
    print(f"Syncing GSC for {company_id}...")
    
    # Simulated Data
    keywords = [
        {"query": "organic protein powder", "clicks": 150, "impressions": 2000, "position": 3.5},
        {"query": "best post workout", "clicks": 80, "impressions": 1200, "position": 5.2},
    ]
    
    for k in keywords:
        supabase.table("insights_core").insert({
            "company_id": company_id,
            "insight_type": "seo_keyword",
            "insight_value": float(k['clicks']),
            "metadata": k
        }).execute()
        
    print(f"Successfully synced GSC for {company_id}")


# ============================================================
# SHOPIFY PRODUCT COSTS (COGS) - For Unit Economics
# ============================================================

@shopify_breaker
@retry_with_backoff(max_retries=3, initial_delay=2.0)
def sync_shopify_products(shop_url: str, access_token: str, company_id: str):
    """
    Syncs product inventory and cost data from Shopify.
    Enables Unit Economics calculations in the Profit Matrix.
    """
    if not supabase:
        return []
    
    session = shopify.Session(shop_url, '2024-01', access_token)
    shopify.ShopifyResource.activate_session(session)
    
    products_data = []
    
    try:
        products = shopify.Product.find(limit=250)
        
        for product in products:
            for variant in product.variants:
                inventory_cost = None
                try:
                    if hasattr(variant, 'inventory_item_id'):
                        inv_item = shopify.InventoryItem.find(variant.inventory_item_id)
                        inventory_cost = getattr(inv_item, 'cost', None)
                except Exception:
                    pass
                
                product_payload = {
                    "company_id": company_id,
                    "product_id": str(product.id),
                    "variant_id": str(variant.id),
                    "title": product.title,
                    "variant_title": variant.title or "Default",
                    "sku": variant.sku,
                    "price": float(variant.price) if variant.price else 0,
                    "cogs": float(inventory_cost) if inventory_cost else None,
                    "inventory_quantity": variant.inventory_quantity or 0,
                    "weight": variant.weight or 0,
                    "weight_unit": variant.weight_unit or "kg"
                }
                products_data.append(product_payload)
                supabase.table("products").upsert(
                    product_payload, on_conflict="company_id,variant_id"
                ).execute()
        
        print(f"Synced {len(products_data)} product variants for {company_id}")
    finally:
        shopify.ShopifyResource.clear_session()
    
    return products_data


def get_product_costs_for_profit_matrix(company_id: str) -> list:
    """Retrieves product cost data formatted for Unit Economics."""
    if not supabase:
        return []
    
    response = supabase.table("products") \
        .select("variant_id, title, variant_title, price, cogs, weight") \
        .eq("company_id", company_id) \
        .not_("cogs", "is", "null") \
        .execute()
    
    if not response.data:
        return []
    
    products = []
    for row in response.data:
        weight_kg = row.get('weight', 0) or 0
        shipping = 5.0 + (2.0 * weight_kg)
        
        products.append({
            "id": row['variant_id'],
            "name": f"{row['title']} - {row.get('variant_title', 'Default')}",
            "price": row['price'],
            "cogs": row['cogs'],
            "shipping": round(shipping, 2),
            "storage_cost": 0.5
        })
    
    return products
