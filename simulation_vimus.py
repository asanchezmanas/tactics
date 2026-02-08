"""
Vimus Profit Simulation - First Client Showcase
Scenario: Vimus (Sports Recovery Brand)
"""

import pandas as pd
import numpy as np
from core.profit import ProfitMatrixEngine

def run_vimus_simulation():
    engine = ProfitMatrixEngine()
    
    print("--- 🚀 VIMUS FIRST CLIENT SIMULATION ---")
    
    # 1. Product Catalog (Vimus)
    products = pd.DataFrame([
        {"id": "VIM-001", "name": "Massage Gun Pro", "price": 199.00, "cogs": 65.00, "shipping": 8.50},
        {"id": "VIM-002", "name": "CBD Recovery Cream", "price": 34.00, "cogs": 6.50, "shipping": 4.00},
        {"id": "VIM-003", "name": "Compression Sleeves", "price": 45.00, "cogs": 9.00, "shipping": 4.00},
        {"id": "VIM-004", "name": "Electrolyte Pack", "price": 29.00, "cogs": 5.00, "shipping": 4.00},
        {"id": "VIM-005", "name": "Yoga Mat Premium", "price": 55.00, "cogs": 12.00, "shipping": 6.50}
    ])
    
    # 2. Simulate 1000 Transactions for Basket Analysis
    np.random.seed(42)
    n_orders = 1000
    transactions = []
    
    for order_id in range(n_orders):
        # High correlation: Massage Gun + CBD Cream
        if np.random.random() < 0.3:
            transactions.append({"order_id": order_id, "product_id": "VIM-001"})
            if np.random.random() < 0.7:
                transactions.append({"order_id": order_id, "product_id": "VIM-002"})
        
        # High correlation: Electrolyte + Compression Sleeves
        if np.random.random() < 0.2:
            transactions.append({"order_id": order_id, "product_id": "VIM-003"})
            if np.random.random() < 0.6:
                transactions.append({"order_id": order_id, "product_id": "VIM-004"})
                
        # Random pick
        if np.random.random() < 0.1:
            transactions.append({"order_id": order_id, "product_id": "VIM-005"})
            
    df_transactions = pd.DataFrame(transactions)
    
    # 3. RUN: Market Basket Analysis
    print("\n🔍 Analizando combinaciones de productos (Market Basket Analysis)...")
    basket_rules = engine.calculate_basket_rules(df_transactions, min_support=0.02)
    
    print("\n💡 TOP BUNDLES RECOMENDADOS (Basado en afinidad):")
    for rule in basket_rules["top_bundles"]:
        # Map IDs to names
        item_names = [products[products['id'] == pid]['name'].values[0] for pid in rule['items']]
        print(f" - {item_names[0]} + {item_names[1]} (Lift: {rule['lift']}, Frecuencia: {rule['frequency']} pedidos)")
    
    # 4. RUN: Unit Economics
    print("\n💰 ANALISIS DE RENTABILIDAD POR PRODUCTO:")
    economics = engine.calculate_unit_economics(products)
    print(economics[['name', 'price', 'gross_margin', 'gross_margin_pct', 'cm1']])
    
    # 5. CROSS-ENGINE: Personalized Bundle for a "VIP AT RISK" customer
    # (Using Engine A's segment to drive Engine C's offer)
    print("\n🎯 OFERTA PERSONALIZADA PARA SEGMENTO: 'VIP_AT_RISK'")
    personalized = engine.get_personalized_bundle("VIP_AT_RISK", economics)
    
    print(f" - Objetivo Estratégico: {personalized['strategy_goal']}")
    print(f" - Lógica: {personalized['logic']}")
    print(f" - Productos Sugeridos: {', '.join(personalized['recommended_items'])}")
    print(f" - Descuento Aplicado: {personalized['applied_discount']*100}%")
    print(f" - Margen Neto Esperado del Bundle: {round(personalized['expected_net_margin'], 2)}€")
    
    print("\n--- ✅ SIMULACION COMPLETADA ---")

if __name__ == "__main__":
    run_vimus_simulation()
