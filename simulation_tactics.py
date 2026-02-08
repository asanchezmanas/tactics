"""
Tactics Self-Simulation - Analyzing the SaaS Business Model
Scenario: Tactics (Marketing AI Infrastructure)
"""

import pandas as pd
import numpy as np
from core.profit import ProfitMatrixEngine

def run_tactics_business_simulation():
    engine = ProfitMatrixEngine()
    
    print("--- 🧠 TACTICS BUSINESS SELF-ANALYSIS ---")
    print("Analizando Tactics como producto: Membresías, Algoritmos y Servicios.")
    
    # 1. Product Catalog (Pure Automated SaaS)
    # COGS = Server Infrastructure + Mathematical Compute (Bayesian MCMC, Tensor ops) + Data Storage
    products = pd.DataFrame([
        {"id": "TAC-CORE", "name": "Tactics Core (Startup)", "price": 199.00, "cogs": 5.00, "shipping": 0.00},
        {"id": "TAC-GROWTH", "name": "Tactics Growth (Scale)", "price": 499.00, "cogs": 15.00, "shipping": 0.00},
        {"id": "TAC-ENT", "name": "Enterprise Unlimited", "price": 1499.00, "cogs": 50.00, "shipping": 0.00},
        {"id": "TAC-SOTA", "name": "SOTA Add-on (Deep Learning)", "price": 250.00, "cogs": 20.00, "shipping": 0.00},
        {"id": "TAC-CONNECT", "name": "Premium Connectors (All-in)", "price": 99.00, "cogs": 2.00, "shipping": 0.00}
    ])
    
    # 2. Simulate 500 Subscriptions
    np.random.seed(42)
    n_orders = 500
    transactions = []
    
    for order_id in range(n_orders):
        # Business Logic: Growth Tier + Premium Connectors is common
        if np.random.random() < 0.4:
            transactions.append({"order_id": order_id, "product_id": "TAC-GROWTH"})
            if np.random.random() < 0.8:
                transactions.append({"order_id": order_id, "product_id": "TAC-CONNECT"})
        
        # Upsell: Enterprise + SOTA
        if np.random.random() < 0.15:
            transactions.append({"order_id": order_id, "product_id": "TAC-ENT"})
            if np.random.random() < 0.9:
                transactions.append({"order_id": order_id, "product_id": "TAC-SOTA"})
                
        # Basic: Core only
        if np.random.random() < 0.3:
            transactions.append({"order_id": order_id, "product_id": "TAC-CORE"})
            
    df_transactions = pd.DataFrame(transactions)
    
    # 3. RUN: Affinities (A qué se suscriben juntos)
    print("\n🔍 Analizando 'Cross-Selling' de Planes Automáticos...")
    basket_rules = engine.calculate_basket_rules(df_transactions, min_support=0.01)
    
    print("\n💡 ESTRATEGIA DE BUNDLING (Puro Producto):")
    for rule in basket_rules["top_bundles"]:
        item_names = [products[products['id'] == pid]['name'].values[0] for pid in rule['items']]
        print(f" - {item_names[0]} + {item_names[1]} (Lift: {rule['lift']}, Support: {rule['support']})")
    
    # 4. RUN: Unit Economics (Escalabilidad 100%)
    print("\n💰 RENTABILIDAD POR PLAN (Unit Economics):")
    economics = engine.calculate_unit_economics(products)
    economics['margin_efficiency'] = (economics['cm1'] / economics['price']) * 100
    print(economics[['name', 'price', 'cm1', 'margin_efficiency']].sort_values('margin_efficiency', ascending=False))
    
    # 5. CROSS-ENGINE: Automated Onboarding Offer
    print("\n🎯 OFERTA AUTOMATICA SEGMENTO: 'NEW_POTENTIAL'")
    personalized = engine.get_personalized_bundle("NEW_POTENTIAL", economics)
    
    print(f" - Misión: {personalized['strategy_goal']}")
    print(f" - Lógica: {personalized['logic']}")
    print(f" - Pack Sugerido: {', '.join(personalized['recommended_items'])}")
    print(f" - Descuento: {personalized['applied_discount']*100}%")
    print(f" - Margen para Tactics (Escalable): {round(personalized['expected_net_margin'], 2)}€")
    
    print("\n--- ✅ TACTICS SELF-ANALYSIS COMPLETE ---")

if __name__ == "__main__":
    run_tactics_business_simulation()
