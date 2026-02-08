import pandas as pd
import numpy as np
from core.engine import DataScienceCore
from core.optimizer import run_budget_optimization, adstock_geometric
from core.segmentation import segment_customers

def test_engine_rfm_preparation():
    engine = DataScienceCore()
    data = {
        'customer_id': ['C1', 'C1', 'C2', 'C1', 'C3'],
        'order_date': ['2023-01-01', '2023-01-02', '2023-01-01', '2023-01-10', '2023-01-15'],
        'revenue': [10, 20, 50, 40, 30]
    }
    df = pd.DataFrame(data)
    rfm = engine.prepare_data(df)
    
    assert len(rfm) == 3
    assert 'frequency' in rfm.columns
    assert 'recency' in rfm.columns
    assert 'T' in rfm.columns
    assert 'monetary_value' in rfm.columns

def test_budget_optimization():
    # alpha (max sales), gamma (saturation rate)
    channel_params = [(1000, 0.8), (2000, 0.5)]
    total_budget = 500
    
    optimal_budgets = run_budget_optimization(total_budget, channel_params)
    
    assert len(optimal_budgets) == 2
    assert abs(sum(optimal_budgets) - total_budget) < 1e-5
    assert all(b >= 0 for b in optimal_budgets)

def test_segmentation():
    data = {
        'prob_alive': [0.9, 0.25, 0.1, 0.9],
        'clv_12m': [100, 500, 50, 1000],
        'expected_purchases_90d': [1, 0.1, 0, 2]
    }
    rfm_pred = pd.DataFrame(data)
    segmented = segment_customers(rfm_pred)
    
    assert 'segmento' in segmented.columns
    assert segmented.iloc[1]['segmento'] == "ALTO RIESGO - VIP"
    assert segmented.iloc[2]['segmento'] == "CLIENTE PERDIDO"
    assert "CLIENTE LEAL" in segmented['segmento'].values


# ===== PHASE 9: PROFIT MATRIX TESTS =====

from core.profit import ProfitMatrixEngine

def test_eclat_basic():
    """Test that ECLAT correctly finds frequent itemsets."""
    engine = ProfitMatrixEngine()
    
    # Create mock transaction data
    # Orders: O1=[A,B], O2=[A,B,C], O3=[A,C], O4=[B,C], O5=[A,B]
    transactions = pd.DataFrame({
        'order_id': ['O1', 'O1', 'O2', 'O2', 'O2', 'O3', 'O3', 'O4', 'O4', 'O5', 'O5'],
        'product_id': ['A', 'B', 'A', 'B', 'C', 'A', 'C', 'B', 'C', 'A', 'B']
    })
    
    # Run ECLAT with low min_support to capture all pairs
    result = engine.run_eclat(transactions, min_support=0.2)
    
    # Check that we get frequent itemsets
    assert len(result) > 0
    
    # {A, B} appears in O1, O2, O5 = 3/5 = 0.6 support
    ab_itemset = [fs for fs, sup in result if fs == frozenset(['A', 'B'])]
    assert len(ab_itemset) == 1


def test_eclat_in_basket_rules():
    """Test that calculate_basket_rules uses ECLAT and returns correct format."""
    engine = ProfitMatrixEngine()
    
    transactions = pd.DataFrame({
        'order_id': ['O1', 'O1', 'O2', 'O2', 'O3', 'O3', 'O4', 'O4'],
        'product_id': ['A', 'B', 'A', 'B', 'A', 'C', 'B', 'C']
    })
    
    result = engine.calculate_basket_rules(transactions, min_support=0.2)
    
    assert 'top_bundles' in result
    assert 'frequent_itemsets' in result
    
    # Should have at least one bundle
    if len(result['top_bundles']) > 0:
        bundle = result['top_bundles'][0]
        assert 'items' in bundle
        assert 'support' in bundle
        assert 'lift' in bundle


def test_thompson_sampling_selection():
    """Test that Thompson Sampling selects an offer."""
    engine = ProfitMatrixEngine()
    
    offers = [
        {'id': 'offer_10_pct', 'name': '10% Off'},
        {'id': 'offer_free_ship', 'name': 'Free Shipping'},
        {'id': 'offer_bundle', 'name': 'Bundle Deal'}
    ]
    
    result = engine.thompson_sampling_select(offers)
    
    assert 'selected_offer' in result
    assert result['selected_offer'] in offers
    assert 'all_samples' in result
    assert len(result['all_samples']) == 3


def test_thompson_sampling_update():
    """Test that Thompson Sampling updates arm priors correctly."""
    engine = ProfitMatrixEngine()
    
    # Simulate 5 successes and 2 failures for an offer
    offer_id = 'offer_test'
    
    for _ in range(5):
        engine.thompson_sampling_update(offer_id, success=True)
    for _ in range(2):
        engine.thompson_sampling_update(offer_id, success=False)
    
    state = engine.get_thompson_state()
    
    assert offer_id in state
    # Alpha should be 1 (initial) + 5 = 6
    assert state[offer_id]['alpha'] == 6.0
    # Beta should be 1 (initial) + 2 = 3
    assert state[offer_id]['beta'] == 3.0
    # Mean should be 6/9 = 0.667
    assert abs(state[offer_id]['mean'] - 0.6667) < 0.01


def test_thompson_state_persistence():
    """Test that Thompson state can be saved and loaded."""
    engine = ProfitMatrixEngine()
    
    # Set up some state
    engine.thompson_sampling_update('A', success=True)
    engine.thompson_sampling_update('A', success=True)
    engine.thompson_sampling_update('B', success=False)
    
    # Get state
    state = engine.get_thompson_state()
    
    # Create new engine and load state
    engine2 = ProfitMatrixEngine()
    engine2.load_thompson_state(state)
    
    state2 = engine2.get_thompson_state()
    assert state2['A']['alpha'] == state['A']['alpha']
    assert state2['B']['beta'] == state['B']['beta']

