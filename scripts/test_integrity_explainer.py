from core.explainers.registry import ExplainerRegistry
from core.explainers.base import ExplainedResult

def test_integrity_explainer():
    print("Testing IntegrityExplainer Registration...")
    registry = ExplainerRegistry()
    explainer = registry.get("integrity")
    assert explainer is not None, "IntegrityExplainer should be registered"
    
    print("\nTesting 'duplicate' explanation...")
    result = explainer.explain("duplicate", 15)
    print(f"Name: {result.metric_name}")
    print(f"Value: {result.formatted_value}")
    print(f"What it means: {result.what_it_means[:100]}...")
    
    assert "con un 100% de certeza" not in result.what_it_means.lower()
    assert "suele ocurrir" in result.what_it_means.lower()
    assert any("ayuda interpretativa" in c for c in result.caveats)
    
    print("\nTesting 'gap' explanation...")
    result = explainer.explain("gap", 5)
    print(f"What it means: {result.what_it_means[:100]}...")
    assert "podría ser" in result.caveats[0].lower() or "podría ser" in result.what_it_means.lower()
    
    print("\nTesting 'critical_nan' explanation...")
    result = explainer.explain("critical_nan", 3)
    print(f"What it means: {result.what_it_means[:100]}...")
    assert "esencial" in result.what_it_means.lower()
    
    print("\nALL INTEGRITY EXPLAINER TESTS PASSED.")

if __name__ == "__main__":
    try:
        test_integrity_explainer()
    except Exception as e:
        print(f"\nTEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
