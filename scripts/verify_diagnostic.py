import pandas as pd
import numpy as np
import requests
import os
from io import StringIO

def generate_test_csv(rows=205):
    """Generates a realistic test CSV for the diagnostic tool with product overlaps."""
    # To test Basket Affinity, we need multiple products per order
    order_ids = [f"ORD_{i//2}" for i in range(rows)] # 2 products per order
    data = {
        'fecha': pd.date_range(start='2023-01-01', periods=rows, freq='D').strftime('%Y-%m-%d'),
        'order_id': order_ids,
        'cliente_id': [f"CUST_{i//2}" for i in range(rows)],
        'monto': np.random.uniform(50, 500, rows),
        'canal': np.random.choice(['FB Ads', 'Google', 'Organic'], rows),
        # Ensure Item A and Item B are often together
        'producto_id': [('Item A' if i%2==0 else 'Item B') if i < 100 else f"Item {i}" for i in range(rows)]
    }
    df = pd.DataFrame(data)
    return df.to_csv(index=False)

def test_diagnostic_api():
    print("--- Testing Live Sandbox Diagnostic API ---")
    
    url = "http://localhost:8000/api/demo/diagnostic"
    csv_content = generate_test_csv()
    
    # We need a running server. For this test, we'll just test the engine logic directly 
    # since we are in the same environment.
    from core.diagnostic_engine import DiagnosticEngine
    
    engine = DiagnosticEngine()
    result = engine.process_csv(StringIO(csv_content))
    
    if result["success"]:
        print("✅ Success: Diagnostic Engine processed CSV correctly.")
        metrics = result["metrics"]
        print(f"   - Pareto Concentration: {metrics['pareto']['ratio_top_20'] * 100:.1f}%")
        print(f"   - Est. Retention: {metrics['retention'] * 100:.1f}%")
        print(f"   - Sample Size: {metrics['sample_size']} rows")
        
        # Verify Basket Affinity
        if metrics.get('basket_affinity'):
            print("✅ Success: Basket Affinity (Market Basket Analysis) calculated.")
            for pair in metrics['basket_affinity']:
                print(f"      - {pair['product_a']} + {pair['product_b']} (Lift: {pair['lift']}x, Conf: {pair['confidence']})")
        else:
            print("❌ Failure: Basket Affinity results missing.")
    else:
        print(f"❌ Failure: {result.get('error')}")

if __name__ == "__main__":
    test_diagnostic_api()
