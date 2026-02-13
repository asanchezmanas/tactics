"""
Verification Script for Elite Explainers (Intelligence 2.0)
Tests that the new elite metrics are correctly interpreted.
"""

import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

from core.explainers.registry import ExplainerRegistry

def test_elite_explainers():
    print("🧠 TESTING ELITE EXPLAINERS (INTELLIGENCE 2.0)")
    print("-" * 50)
    
    registry = ExplainerRegistry()
    
    # 1. Test LTV Elite Metrics
    print("\n[A] LTV Elite Metrics:")
    ltv_metrics = ["revenue_velocity", "attention_weight"]
    for m_id in ltv_metrics:
        explanation = registry.explain("ltv", m_id, 0.75)
        print(f"✅ Metric: {explanation.metric_name}")
        print(f"   What it means: {explanation.what_it_means[:80]}...")
        if not explanation.what_it_means:
            print(f"❌ FAILED: No explanation found for {m_id}")

    # 2. Test MMM Elite Metrics
    print("\n[B] MMM Elite Metrics:")
    mmm_metrics = ["synergy_index", "multi_objective_balance"]
    for m_id in mmm_metrics:
        explanation = registry.explain("mmm", m_id, 2.5)
        print(f"✅ Metric: {explanation.metric_name}")
        print(f"   What it means: {explanation.what_it_means[:80]}...")
        if not explanation.what_it_means:
            print(f"❌ FAILED: No explanation found for {m_id}")

    print("-" * 50)
    print("✨ VERIFICATION COMPLETE")

if __name__ == "__main__":
    test_elite_explainers()
