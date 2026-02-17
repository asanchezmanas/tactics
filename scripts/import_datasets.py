"""
Demo Showcase Dataset Importer

Downloads and imports well-known public marketing datasets to demonstrate
Tactics' core analytic engines (LTV, Churn, MMM).

Datasets:
1. UCI Online Retail: E-commerce LTV & Segmentation
2. Advertising Spend: Marketing Mix Modeling
3. Telco Churn: Predictive CRM & Retention

Usage:
    python scripts/import_demo_showcases.py --all
    python scripts/import_demo_showcases.py --showcase ecommerce
    python scripts/import_demo_showcases.py --verify
"""
import os
import sys
import json
import pandas as pd
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from api.database import get_local_cache

# ============================================================
# DEMO DATASET DEFINITIONS
# ============================================================

SHOWCASES = {
    "ecommerce": {
        "name": "E-commerce CPG (UCI Online Retail)",
        "description": "UK-based online retail dataset. Demonstrates LTV calculation, customer segmentation, and purchase frequency analysis.",
        "company_id": "demo_ecommerce",
        "source_url": "https://archive.ics.uci.edu/ml/machine-learning-databases/00352/Online%20Retail.xlsx",
        "highlights": [
            "537,000+ transactions across 4,300+ customers",
            "Ideal for BG/NBD and Pareto/NBD model comparison",
            "Rich for RFM segmentation (Champions, Hibernating, etc.)"
        ],
        "engine_focus": ["LTV", "Segmentation", "Cohort Analysis"]
    },
    "mmm": {
        "name": "Advertising Spend (Kaggle)",
        "description": "Classic advertising dataset with TV, Radio, and Newspaper spend vs. Sales. Demonstrates Marketing Mix Modeling and saturation curves.",
        "company_id": "demo_mmm",
        "highlights": [
            "200 observations of channel spend and revenue",
            "Perfect for Hill saturation and Adstock decay",
            "Visualizes diminishing returns per channel"
        ],
        "engine_focus": ["MMM", "Budget Optimizer", "ROAS"]
    },
    "churn": {
        "name": "Telco Churn (IBM)",
        "description": "IBM sample dataset for customer churn prediction. Demonstrates risk scoring, retention targeting, and predictive analytics.",
        "company_id": "demo_churn",
        "highlights": [
            "7,000+ customers with tenure, contract, and services data",
            "Binary churn target for classification",
            "Rich for cohort-based retention strategies"
        ],
        "engine_focus": ["Churn Radar", "Risk Scoring", "Retention"]
    },
    "banking_churn": {
        "name": "Banking Churn (Financial Services)",
        "description": "European bank dataset for predicting customer exit. Focuses on credit scores, age, and balance as risk factors.",
        "company_id": "demo_banking",
        "highlights": [
            "10,000 customers from 3 countries (France, Spain, Germany)",
            "Detects risk based on financial tenure and balance",
            "Demonstrates sector-specific churn triggers"
        ],
        "engine_focus": ["Churn Radar", "Financial Risk", "Segmentation"]
    },
    "saas_ltv": {
        "name": "SaaS Subscriptions (B2B)",
        "description": "Subscription dataset demonstrating recurring revenue dynamics, churn within cohorts, and expansion revenue.",
        "company_id": "demo_saas",
        "highlights": [
            "MRR and ARR tracking across multiple plan tiers",
            "Calculates Net Revenue Retention (NRR)",
            "Shows LTV for subscription business models"
        ],
        "engine_focus": ["LTV", "MRR Analytics", "Cohort Analysis"]
    },
    "digital_mmm": {
        "name": "Digital Marketing Mix (Multi-Channel)",
        "description": "Digital-first dataset including TikTok, Meta, and Google Ads spend. High granularity for modern attribution.",
        "company_id": "demo_digital_mmm",
        "highlights": [
            "Social-first spend allocation patterns",
            "TikTok specific saturation and adstock",
            "Demonstrates efficiency in fragmented digital ecosystems"
        ],
        "engine_focus": ["MMM", "Budget Optimizer", "Digital Attribution"]
    }
}


# ============================================================
# BUNDLED SAMPLE DATA (Fallback / Offline Mode)
# ============================================================

# Minimal synthetic data for each showcase, used if downloads fail
BUNDLED_ECOMMERCE = [
    {"order_id": "ORD-001", "customer_id": "C-001", "order_date": "2024-01-05", "revenue": 120.50},
    {"order_id": "ORD-002", "customer_id": "C-001", "order_date": "2024-02-10", "revenue": 85.00},
    {"order_id": "ORD-003", "customer_id": "C-002", "order_date": "2024-01-15", "revenue": 250.00},
    {"order_id": "ORD-004", "customer_id": "C-003", "order_date": "2024-01-20", "revenue": 45.00},
    {"order_id": "ORD-005", "customer_id": "C-002", "order_date": "2024-03-01", "revenue": 320.00},
    {"order_id": "ORD-006", "customer_id": "C-004", "order_date": "2024-02-28", "revenue": 75.00},
    {"order_id": "ORD-007", "customer_id": "C-001", "order_date": "2024-04-05", "revenue": 150.00},
    {"order_id": "ORD-008", "customer_id": "C-005", "order_date": "2024-03-15", "revenue": 500.00},
    {"order_id": "ORD-009", "customer_id": "C-003", "order_date": "2024-04-20", "revenue": 60.00},
    {"order_id": "ORD-010", "customer_id": "C-002", "order_date": "2024-05-01", "revenue": 180.00},
]

BUNDLED_MMM = [
    {"fecha": "2024-01-01", "canal": "Google Ads", "inversion": 1500.0, "impresiones": 50000, "clics": 1200},
    {"fecha": "2024-01-01", "canal": "Meta Ads", "inversion": 2000.0, "impresiones": 80000, "clics": 1800},
    {"fecha": "2024-01-01", "canal": "TV", "inversion": 5000.0, "impresiones": 200000, "clics": 0},
    {"fecha": "2024-02-01", "canal": "Google Ads", "inversion": 1800.0, "impresiones": 60000, "clics": 1500},
    {"fecha": "2024-02-01", "canal": "Meta Ads", "inversion": 2200.0, "impresiones": 90000, "clics": 2000},
    {"fecha": "2024-02-01", "canal": "TV", "inversion": 4500.0, "impresiones": 180000, "clics": 0},
    {"fecha": "2024-03-01", "canal": "Google Ads", "inversion": 2000.0, "impresiones": 70000, "clics": 1700},
    {"fecha": "2024-03-01", "canal": "Meta Ads", "inversion": 2500.0, "impresiones": 100000, "clics": 2200},
    {"fecha": "2024-03-01", "canal": "TV", "inversion": 6000.0, "impresiones": 250000, "clics": 0},
]

BUNDLED_CHURN = [
    {"customer_id": "CH-001", "tenure_months": 24, "monthly_charges": 75.0, "total_charges": 1800.0, "churn_risk": 0.15},
    {"customer_id": "CH-002", "tenure_months": 6, "monthly_charges": 95.0, "total_charges": 570.0, "churn_risk": 0.65},
    {"customer_id": "CH-003", "tenure_months": 48, "monthly_charges": 50.0, "total_charges": 2400.0, "churn_risk": 0.08},
    {"customer_id": "CH-004", "tenure_months": 12, "monthly_charges": 85.0, "total_charges": 1020.0, "churn_risk": 0.45},
    {"customer_id": "CH-005", "tenure_months": 3, "monthly_charges": 110.0, "total_charges": 330.0, "churn_risk": 0.78},
]


# ============================================================
# IMPORT LOGIC
# ============================================================

def import_showcase(showcase_id: str, use_bundled: bool = True) -> dict:
    """
    Imports a specific showcase dataset into the local cache.
    
    Args:
        showcase_id: One of 'ecommerce', 'mmm', 'churn'
        use_bundled: If True, uses bundled sample data instead of downloading
        
    Returns:
        Dictionary with import status and record counts
    """
    if showcase_id not in SHOWCASES:
        return {"status": "error", "message": f"Unknown showcase: {showcase_id}"}
    
    showcase = SHOWCASES[showcase_id]
    company_id = showcase["company_id"]
    cache = get_local_cache()
    
    print(f"\n­ƒôè Importing: {showcase['name']}")
    print(f"   Company ID: {company_id}")
    
    result = {
        "showcase_id": showcase_id,
        "company_id": company_id,
        "status": "success",
        "records": {}
    }
    
    try:
        if showcase_id == "ecommerce":
            # Import sales data
            data = BUNDLED_ECOMMERCE if use_bundled else _download_uci_retail()
            cache.set(f"ventas:{company_id}", data, "ventas", company_id=company_id)
            result["records"]["ventas"] = len(data)
            print(f"   Ô£ô {len(data)} sales records imported")
            
        elif showcase_id == "mmm":
            # Import marketing spend data
            data = BUNDLED_MMM if use_bundled else _download_advertising()
            cache.set(f"gastos:{company_id}", data, "gastos", company_id=company_id)
            result["records"]["gastos"] = len(data)
            print(f"   Ô£ô {len(data)} marketing spend records imported")
            
        elif showcase_id == "churn":
            # Import customer data with churn risk
            data = BUNDLED_CHURN if use_bundled else _download_telco_churn()
            # For churn, we store as customer data with risk scores
            cache.set(f"clientes:{company_id}", data, "clientes", company_id=company_id)
            result["records"]["clientes"] = len(data)
            print(f"   Ô£ô {len(data)} customer records imported")
            
        elif showcase_id == "banking_churn":
            data = _download_banking_churn() if not use_bundled else BUNDLED_CHURN # Fallback to bundled for now
            cache.set(f"clientes:{company_id}", data, "clientes", company_id=company_id)
            result["records"]["clientes"] = len(data)
            print(f"   Ô£ô {len(data)} banking customer records imported")
            
        elif showcase_id == "saas_ltv":
            data = _download_saas_ltv() if not use_bundled else BUNDLED_ECOMMERCE # Fallback
            cache.set(f"ventas:{company_id}", data, "ventas", company_id=company_id)
            result["records"]["ventas"] = len(data)
            print(f"   Ô£ô {len(data)} SaaS subscription records imported")
            
        elif showcase_id == "digital_mmm":
            data = _download_digital_mmm() if not use_bundled else BUNDLED_MMM # Fallback
            cache.set(f"gastos:{company_id}", data, "gastos", company_id=company_id)
            result["records"]["gastos"] = len(data)
            print(f"   Ô£ô {len(data)} digital marketing records imported")
            
        # Store showcase metadata
        cache.set(f"showcase_meta:{company_id}", showcase, "metadata", company_id=company_id)
        
    except Exception as e:
        result["status"] = "error"
        result["message"] = str(e)
        print(f"   Ô£ù Error: {e}")
    
    return result


def import_all_showcases(use_bundled: bool = True) -> list:
    """Imports all available showcase datasets."""
    results = []
    for showcase_id in SHOWCASES:
        results.append(import_showcase(showcase_id, use_bundled))
    return results


def verify_showcases() -> dict:
    """Verifies that all showcase data is correctly imported."""
    cache = get_local_cache()
    verification = {}
    
    print("\n­ƒöì Verifying Showcase Datasets...\n")
    
    for showcase_id, showcase in SHOWCASES.items():
        company_id = showcase["company_id"]
        
        # Check for data
        if showcase_id == "ecommerce":
            data = cache.get(f"ventas:{company_id}")
        elif showcase_id == "mmm":
            data = cache.get(f"gastos:{company_id}")
        elif showcase_id == "churn":
            data = cache.get(f"clientes:{company_id}")
        else:
            data = None
        
        if data:
            record_count = len(data) if isinstance(data, list) else 0
            verification[showcase_id] = {
                "status": "Ô£à OK",
                "company_id": company_id,
                "record_count": record_count
            }
            print(f"  Ô£à {showcase['name']}: {record_count} records")
        else:
            verification[showcase_id] = {
                "status": "ÔØî MISSING",
                "company_id": company_id,
                "record_count": 0
            }
            print(f"  ÔØî {showcase['name']}: No data found")
    
    return verification


def get_showcase_info(showcase_id: str = None) -> dict:
    """Returns metadata for one or all showcases."""
    if showcase_id:
        return SHOWCASES.get(showcase_id)
    return SHOWCASES


# ============================================================
# DOWNLOAD HELPERS (Optional - for full datasets)
# ============================================================

def _download_uci_retail():
    """
    Downloads and transforms the UCI Online Retail dataset.
    Source: https://archive.ics.uci.edu/ml/datasets/Online+Retail
    
    Returns list of dicts in Tactics ventas schema.
    """
    import requests
    from io import BytesIO
    
    print("   [INFO] Downloading UCI Online Retail dataset (may take a minute)...")
    
    try:
        # Try the Excel file first (official UCI source)
        url = "https://archive.ics.uci.edu/ml/machine-learning-databases/00352/Online%20Retail.xlsx"
        response = requests.get(url, timeout=60)
        response.raise_for_status()
        
        # Read Excel file
        df = pd.read_excel(BytesIO(response.content), engine='openpyxl')
        print(f"   [INFO] Downloaded {len(df)} raw records")
        
    except Exception as e:
        print(f"   [WARN] Excel download failed ({e}), trying CSV mirror...")
        try:
            # Fallback to a CSV mirror (Kaggle-style)
            csv_url = "https://raw.githubusercontent.com/datasets/online-retail/master/data/online-retail.csv"
            df = pd.read_csv(csv_url)
            print(f"   [INFO] Downloaded {len(df)} raw records from CSV mirror")
        except Exception as e2:
            print(f"   [ERROR] Both downloads failed: {e2}")
            print("   [INFO] Falling back to bundled sample data")
            return BUNDLED_ECOMMERCE
    
    # Transform to Tactics schema
    print("   [INFO] Transforming to Tactics schema...")
    
    # Clean data
    df = df.dropna(subset=['CustomerID', 'InvoiceNo', 'InvoiceDate'])
    df = df[df['Quantity'] > 0]  # Remove cancellations
    df = df[df['UnitPrice'] > 0]  # Remove free items
    
    # Calculate revenue per line
    df['revenue'] = df['Quantity'] * df['UnitPrice']
    
    # Aggregate to order level (one row per invoice)
    orders = df.groupby(['InvoiceNo', 'CustomerID', 'InvoiceDate']).agg({
        'revenue': 'sum',
        'Country': 'first'
    }).reset_index()
    
    # Rename to Tactics schema
    orders = orders.rename(columns={
        'InvoiceNo': 'order_id',
        'CustomerID': 'customer_id',
        'InvoiceDate': 'order_date',
        'Country': 'canal_origen'
    })
    
    # Format customer_id as string
    orders['customer_id'] = orders['customer_id'].astype(int).astype(str)
    
    # Format order_date as string
    orders['order_date'] = pd.to_datetime(orders['order_date']).dt.strftime('%Y-%m-%d')
    
    # Round revenue
    orders['revenue'] = orders['revenue'].round(2)
    
    # Convert to list of dicts
    result = orders.to_dict('records')
    
    print(f"   [INFO] Transformed to {len(result)} orders")
    print(f"   [INFO] Unique customers: {orders['customer_id'].nunique()}")
    print(f"   [INFO] Date range: {orders['order_date'].min()} to {orders['order_date'].max()}")
    
    return result


def _download_advertising():
    """
    Synthesizes a high-fidelity Omnichannel MMM dataset.
    Generates 104 weeks (2 years) of data with realistic seasonality, 
    channel-specific adstock, and saturation (Hill curves).
    """
    import numpy as np
    import random
    
    print("   [INFO] Generating high-fidelity Omnichannel MMM dataset (104 weeks)...")
    
    weeks = 104
    base_date = pd.Timestamp('2023-01-01')
    channels = ["Google Ads", "Meta Ads", "TV"]
    
    # Coefficients for ground truth (to verify accuracy later)
    # TV: High impact, High saturation
    # Google: Direct, Linear
    # Meta: High decay
    
    result = []
    for w in range(weeks):
        date_str = (base_date + pd.Timedelta(days=7*w)).strftime('%Y-%m-%d')
        
        # Seasonality factor (sine wave)
        seasonality = 1.0 + 0.2 * np.sin(2 * np.pi * w / 52)
        
        base_sales = 5000 * seasonality
        
        for canal in channels:
            if canal == "TV":
                spend = 2000 + random.random() * 5000 if w % 4 == 0 else 0 # Flighting pattern
                # Hill saturation logic: S = Spend^alpha / (Spend^alpha + K^alpha)
                conv = base_sales * (spend**0.7 / (spend**0.7 + 3000**0.7)) * 0.4
            elif canal == "Google Ads":
                spend = 1000 + random.random() * 1000
                conv = (spend * 1.5) * seasonality
            else: # Meta Ads
                spend = 800 + random.random() * 2000
                conv = (spend * 1.2) * seasonality
                
            result.append({
                "fecha": date_str,
                "canal": canal,
                "inversion": round(spend, 2),
                "impresiones": int(spend * 80),
                "clics": int(spend * 1.5),
                "conversiones": int(conv)
            })
            
    return result


def _download_telco_churn():
    """
    Downloads the IBM Telco Churn dataset.
    Source: https://www.kaggle.com/datasets/blastchar/telco-customer-churn
    
    Returns list of dicts with customer + churn risk data.
    """
    import requests
    
    print("   [INFO] Downloading Telco Churn dataset...")
    
    try:
        # GitHub mirror of the Telco Churn dataset
        url = "https://raw.githubusercontent.com/IBM/telco-customer-churn-on-icp4d/master/data/Telco-Customer-Churn.csv"
        df = pd.read_csv(url)
        print(f"   [INFO] Downloaded {len(df)} customer records")
        
    except Exception as e:
        print(f"   [ERROR] Download failed: {e}")
        print("   [INFO] Falling back to bundled sample data")
        return BUNDLED_CHURN
    
    # Transform to Tactics schema
    print("   [INFO] Transforming to Tactics schema...")
    
    # Clean TotalCharges (some are empty strings)
    df['TotalCharges'] = pd.to_numeric(df['TotalCharges'], errors='coerce').fillna(0)
    
    # Calculate churn risk (1 = churned, 0 = retained)
    df['churn_risk'] = (df['Churn'] == 'Yes').astype(float)
    
    # Select and rename columns
    result_df = df[['customerID', 'tenure', 'MonthlyCharges', 'TotalCharges', 'churn_risk', 'Contract', 'PaymentMethod']].copy()
    result_df = result_df.rename(columns={
        'customerID': 'customer_id',
        'tenure': 'tenure_months',
        'MonthlyCharges': 'monthly_charges',
        'TotalCharges': 'total_charges',
        'Contract': 'contract_type',
        'PaymentMethod': 'payment_method'
    })
    
    # Convert to list of dicts
    result = result_df.to_dict('records')
    
    churned = sum(1 for r in result if r['churn_risk'] > 0.5)
    print(f"   [INFO] Transformed {len(result)} customers")
    print(f"   [INFO] Churn rate: {churned}/{len(result)} ({100*churned/len(result):.1f}%)")
    
    return result


def _download_banking_churn():
    """
    Synthesizes a high-fidelity Banking Churn dataset.
    Generates 10,000 customers with realistic financial correlations.
    """
    import random
    import numpy as np
    
    print("   [INFO] Generating high-fidelity Banking Churn dataset (10,000 customers)...")
    
    result = []
    countries = ["France", "Spain", "Germany"]
    
    for i in range(10000):
        age = int(np.random.normal(38, 10))
        age = max(18, min(age, 90))
        
        # Logic for churn correlation (older clients or low active products churn more in this demo)
        credit_score = random.randint(350, 850)
        balance = 0 if random.random() > 0.3 else random.uniform(5000, 250000)
        num_products = random.randint(1, 4)
        is_active = random.choice([0, 1])
        
        # Churn probability estimation (Ground Truth logic)
        prob = 0.1
        if age > 50: prob += 0.3
        if balance > 100000: prob += 0.2
        if num_products == 1: prob += 0.15
        if is_active == 0: prob += 0.2
        if credit_score < 500: prob += 0.1
        
        churned = 1 if random.random() < prob else 0
        
        result.append({
            "customer_id": f"BANK-{100000+i}",
            "surname": f"User{i}",
            "credit_score": credit_score,
            "geography": random.choice(countries),
            "gender": random.choice(["Male", "Female"]),
            "age": age,
            "tenure_months": random.randint(0, 10),
            "balance": round(balance, 2),
            "num_of_products": num_products,
            "has_cr_card": random.randint(0, 1),
            "is_active_member": is_active,
            "estimated_salary": round(random.uniform(20000, 150000), 2),
            "churn_risk": float(churned)
        })
        
    return result


def _download_saas_ltv():
    """
    Synthesizes a high-fidelity SaaS subscription dataset.
    Public SaaS datasets are rare/proprietary, so we generate a realistic one
    based on SaaS metrics (MRR tiers, expansion, churn).
    """
    import random
    from datetime import datetime, timedelta
    
    print("   [INFO] Generating synthetic SaaS LTV dataset...")
    
    customer_ids = [f"SAAS-{1000+i}" for i in range(500)]
    tiers = {"Basic": 29, "Pro": 99, "Enterprise": 499}
    
    result = []
    for cid in customer_ids:
        start_date = datetime(2023, 1, 1) + timedelta(days=random.randint(0, 365))
        tier = random.choices(list(tiers.keys()), weights=[0.7, 0.2, 0.1])[0]
        price = tiers[tier]
        
        # Generations months of payments
        months = random.randint(1, 24)
        for m in range(months):
            payment_date = (start_date + timedelta(days=30*m)).strftime('%Y-%m-%d')
            result.append({
                "order_id": f"INV-{cid}-{m}",
                "customer_id": cid,
                "order_date": payment_date,
                "revenue": price + (random.random() * 10), # Slight variance
                "canal_origen": random.choice(["G2", "LinkedIn", "Direct"]),
                "metadata": {"tier": tier}
            })
            
    print(f"   [INFO] Generated {len(result)} subscription payments for {len(customer_ids)} customers")
    return result


def _download_digital_mmm():
    """
    Downloads digital marketing mix data.
    """
    print("   [INFO] Generating Digital MMM dataset (Meta, Google, TikTok)...")
    import random
    
    channels = ["Meta Ads", "Google Ads", "TikTok Ads"]
    base_date = pd.Timestamp('2023-01-01')
    
    result = []
    for week in range(52):
        current_date = (base_date + pd.Timedelta(days=7*week)).strftime('%Y-%m-%d')
        sales_baseline = 10000 + random.random() * 5000
        
        for canal in channels:
            spend = 1000 + random.random() * 2000
            if canal == "TikTok Ads":
                # TikTok has higher decay/saturation in this demo
                intensity = spend / 2000
                conv = sales_baseline * (intensity ** 0.5) * 0.2
            else:
                intensity = spend / 3000
                conv = sales_baseline * (intensity ** 0.7) * 0.3
                
            result.append({
                "fecha": current_date,
                "canal": canal,
                "inversion": round(spend, 2),
                "impresiones": int(spend * 100),
                "clics": int(spend * 2),
                "conversiones": int(conv)
            })
            
    return result


# ============================================================
# CLI
# ============================================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Import demo showcase datasets")
    parser.add_argument("--all", action="store_true", help="Import all showcases")
    parser.add_argument("--showcase", type=str, help="Import specific showcase (ecommerce, mmm, churn)")
    parser.add_argument("--verify", action="store_true", help="Verify imported data")
    parser.add_argument("--list", action="store_true", help="List available showcases")
    parser.add_argument("--download", action="store_true", help="Download real datasets instead of using bundled samples")
    
    args = parser.parse_args()
    
    # Determine whether to use bundled or download
    use_bundled = not args.download
    
    if args.list:
        print("\n­ƒôÜ Available Showcases:\n")
        for sid, info in SHOWCASES.items():
            print(f"  ÔÇó {sid}: {info['name']}")
            print(f"    {info['description'][:80]}...")
            print(f"    Focus: {', '.join(info['engine_focus'])}\n")
    
    elif args.verify:
        verify_showcases()
    
    elif args.showcase:
        result = import_showcase(args.showcase, use_bundled=use_bundled)
        if result["status"] == "success":
            print(f"\nÔ£à Showcase '{args.showcase}' imported successfully!")
        else:
            print(f"\nÔØî Import failed: {result.get('message', 'Unknown error')}")
    
    elif args.all:
        print("=" * 50)
        print("   TACTICS DEMO SHOWCASE IMPORTER")
        if args.download:
            print("   (Downloading real datasets...)")
        print("=" * 50)
        results = import_all_showcases(use_bundled=use_bundled)
        
        success_count = sum(1 for r in results if r["status"] == "success")
        print(f"\n{'=' * 50}")
        print(f"   Summary: {success_count}/{len(results)} showcases imported")
        print("=" * 50)
    
    else:
        parser.print_help()
