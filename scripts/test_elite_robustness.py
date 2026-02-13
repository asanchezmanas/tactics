"""
Robustness Stress Test - Tactics Intelligence 2.0
Simulates volatile data and outliers to verify Elite Algorithm resilience.
"""

import pandas as pd
import numpy as np
import os
import sys
import warnings

# Add project root to path
sys.path.append(os.getcwd())

from core.features import EliteFeatures
from core.engine_enterprise import EnterpriseDataScienceCore

# Suppress warnings for cleaner output
warnings.filterwarnings('ignore')

def generate_dirty_data(n_customers=100, n_months=24):
    """Generates synthetic data with intentional noise and outliers."""
    data = []
    for c in range(n_customers):
        # Base behavior
        base_rev = np.random.uniform(50, 200)
        for m in range(n_months):
            # Normal variance
            rev = base_rev * np.random.normal(1, 0.2)
            
            # Add "Whale" outliers (1% chance)
            if np.random.random() < 0.01:
                rev *= 50 # massive spike
                
            # Add "Dead periods" (5% chance)
            if np.random.random() < 0.05:
                rev = 0
                
            data.append({
                'customer_id': f'CUST_{c}',
                'order_date': pd.Timestamp('2024-01-01') + pd.DateOffset(months=m),
                'revenue': max(0, rev)
            })
    return pd.DataFrame(data)

def test_elite_pipeline():
    print("🚀 Starting Elite Robustness Stress Test...")
    
    # 1. Generate Data
    df = generate_dirty_data()
    print(f"✅ Generated {len(df)} transactions for {df['customer_id'].nunique()} customers.")
    
    # 2. Test Feature Engineering (Robustness)
    engineer = EliteFeatures(company_id="test_elite")
    cinematic = engineer.calculate_cinematic_features(df)
    
    # Check for Inf/NaN in velocity
    if cinematic['avg_velocity'].isin([np.inf, -np.inf]).any() or cinematic['avg_velocity'].isna().any():
        print("❌ Feature Engineering failed: Nan/Inf detected in velocity.")
    else:
        print("✅ Cinematic Features: No NaN/Inf detected under stress.")
        
    # Scale and check distribution
    scaled = engineer.robust_scaling(cinematic, ['avg_velocity', 'total_revenue'])
    v_max = scaled['avg_velocity'].max()
    print(f"📊 Robust Scaling: Velocity Max={v_max:.2f} (Legacy would be much higher)")
    
    # 3. Test LSTM + Attention (Inference)
    engine = EnterpriseDataScienceCore(sequence_length=12)
    # Mock sequence data for quick test (10 customers, 12 months, 5 features)
    X = np.random.normal(0, 1, (10, 12, 5)) 
    
    try:
        # Build model
        model = engine.build_lstm_attention_model(n_features=5)
        print("✅ LSTM + Attention Model: Architecture compiled successfully.")
        
        # Test inference
        preds = engine.predict_lstm(X)
        if len(preds['predictions']) == 10:
            print("✅ Inference: Successfully generated LTV predictions.")
        else:
            print(f"❌ Inference: Unexpected output shape ({len(preds['predictions'])}).")
            
    except Exception as e:
        print(f"❌ Model Test Failed: {str(e)}")

if __name__ == "__main__":
    test_elite_pipeline()
