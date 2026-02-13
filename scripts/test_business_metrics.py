"""
Verification: Advanced Business Metrics & AI Feedback Loop
Tests the derivation of high-level metrics and their injection into the AI engines.
"""

import pandas as pd
import numpy as np
import os
import sys
from datetime import datetime, timedelta

# Add project root to path
sys.path.append(os.getcwd())

from core.metrics_factory import BusinessMetricsFactory
from core.engine_enterprise import EnterpriseDataScienceCore
from core.optimizer_enterprise import EnterpriseMMOptimizer

def generate_mock_data():
    """Generates synthetic data for testing."""
    dates = [datetime.now() - timedelta(days=i) for i in range(120, 0, -1)]
    
    # Sales data
    sales = []
    customers = [f"cust_{i}" for i in range(20)]
    channels = ["Meta Ads", "Google Ads", "Organic"]
    products = ["prod_Premium", "prod_Basic", "prod_Starter"]
    
    for d in dates:
        if np.random.random() > 0.3:
            sales.append({
                "order_id": f"ord_{d.strftime('%Y%m%d%H%M')}",
                "customer_id": np.random.choice(customers),
                "order_date": d,
                "revenue": np.random.uniform(20, 150),
                "canal": np.random.choice(channels),
                "product_id": np.random.choice(products)
            })
    sales_df = pd.DataFrame(sales)
    
    # Marketing data
    marketing = []
    for d in dates:
        for ch in ["Meta Ads", "Google Ads"]:
            marketing.append({
                "fecha": d,
                "canal": ch,
                "inversion": 50.0
            })
    marketing_df = pd.DataFrame(marketing)
    
    return sales_df, marketing_df

def test_metrics_calculation():
    print("--- Testing Metrics Calculation (Intelligence 2.0) ---")
    sales_df, marketing_df = generate_mock_data()
    factory = BusinessMetricsFactory("test_company")
    report = factory.calculate_all(sales_df, marketing_df)
    
    print(f"MER Lifetime: {report.efficiency['mer_lifetime']}")
    print(f"POAS: {report.deep_synthesis['poas']}")
    print(f"Pareto Concentration (Ratio Top 20%): {report.deep_synthesis['pareto_concentration']['ratio_top_20']}")
    print(f"iROAS Estimate: {report.deep_synthesis.get('incremental_roas_estimate', 'N/A')}")
    print(f"High Value Products (Gateways): {report.signals_for_ai['high_value_products']}")
    
    # Test Normalization
    test_norm = factory._normalize_canal("Facebook Ads")
    print(f"Normalization Test ('Facebook Ads' -> '{test_norm}')")
    assert test_norm == "meta"
    
    assert report.efficiency['mer_lifetime'] > 0
    assert report.deep_synthesis['poas'] >= 0
    assert report.deep_synthesis['pareto_concentration']['ratio_top_20'] <= 1
    
    print("✅ Deep Synthesis derivation successful.")
    return report.signals_for_ai

def test_ai_reinforcement(signals):
    print("\n--- Testing AI Reinforcement (Feedback Loop) ---")
    
    # 1. Engine A (LTV) reinforcement
    engine = EnterpriseDataScienceCore()
    # Mock sequence data (1 customer, 12 months, 5 features)
    X = np.random.random((5, 12, 5))
    y = np.random.random((5,))
    
    # Train fallback model so predict works
    engine._fallback_train(X, y)
    
    # Run prediction with retention_bias (using one sample)
    X_single = X[:1]
    preds_biased = engine.predict_lstm(X_single, retention_bias=signals['retention_bias'])
    
    print(f"LTV with Retention Bias ({signals['retention_bias']}): {preds_biased['predictions'][0]:.2f}")
    print(f"LTV Reinforcement Reason: {preds_biased.get('reinforcement_reason')}")
    
    assert "reinforcement_reason" in preds_biased
    assert "retención" in preds_biased["reinforcement_reason"]

    # 2. Engine B (MMM) reinforcement
    optimizer = EnterpriseMMOptimizer()
    spend = np.random.random((10, 3)) # 10 periods, 3 channels
    revenue = np.random.random((10,))
    
    # Run inference with MER prior
    results = optimizer.run_pymc_inference(
        spend, revenue, ["Meta", "Google", "TikTok"],
        n_samples=100, # Fast test
        mer_prior=signals['mer_historical_prior']
    )
    
    print(f"MMM Reinforcement Reason: {results.get('reinforcement_reason')}")
    assert "reinforcement_reason" in results
    assert "Bayesiano" in results["reinforcement_reason"] or "heurístico" in results["reinforcement_reason"]
    print("✅ AI Engines successfully accepted reinforcement signals.")

if __name__ == "__main__":
    try:
        signals = test_metrics_calculation()
        test_ai_reinforcement(signals)
        print("\n✨ ALL TESTS PASSED: Business Metrics + AI Feedback Loop is functional.")
    except Exception as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
