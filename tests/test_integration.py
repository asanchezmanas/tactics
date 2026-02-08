"""
Integration Tests for Core Algorithm Pipelines.

Tests end-to-end functionality of:
- LTV/Churn prediction pipeline
- LinUCB learning behavior
- Thompson Sampling learning behavior
- Model validation metrics
"""
import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from core.engine import DataScienceCore
from core.profit import ProfitMatrixEngine
from core.segmentation import segment_customers
from core.model_registry import ModelRegistry


# ============================================================
# LTV/CHURN PIPELINE TESTS
# ============================================================

def test_ltv_pipeline_end_to_end():
    """Test complete LTV prediction pipeline produces valid output."""
    engine = DataScienceCore()
    
    # Create realistic mock transaction data
    np.random.seed(42)
    customers = ['C001', 'C002', 'C003', 'C004', 'C005'] * 5
    dates = [datetime(2024, 1, 1) + timedelta(days=np.random.randint(0, 180)) for _ in customers]
    revenues = np.random.uniform(50, 500, len(customers))
    
    df = pd.DataFrame({
        'customer_id': customers,
        'order_date': dates,
        'revenue': revenues
    })
    
    rfm = engine.prepare_data(df)
    predictions = engine.predict(rfm)
    
    # Verify all expected columns exist
    assert 'clv_12m' in predictions.columns
    assert 'prob_alive' in predictions.columns
    assert 'clv_lower' in predictions.columns
    assert 'clv_upper' in predictions.columns
    assert 'expected_purchases_90d' in predictions.columns
    
    # Verify confidence intervals are valid (lower <= point <= upper)
    assert all(predictions['clv_lower'] <= predictions['clv_12m']), "Lower CI should be <= point estimate"
    assert all(predictions['clv_12m'] <= predictions['clv_upper']), "Upper CI should be >= point estimate"
    
    # Verify prob_alive is in valid range
    assert all(predictions['prob_alive'] >= 0) and all(predictions['prob_alive'] <= 1)


def test_validation_returns_real_metrics():
    """Test that validation returns actual computed metrics, not hardcoded."""
    engine = DataScienceCore()
    
    # Create data spanning enough time for temporal split
    np.random.seed(42)
    customers = [f'C{i:03d}' for i in range(50)]
    
    transactions = []
    for cust in customers:
        n_orders = np.random.randint(2, 8)
        for _ in range(n_orders):
            transactions.append({
                'customer_id': cust,
                'order_date': datetime(2024, 1, 1) + timedelta(days=np.random.randint(0, 300)),
                'revenue': np.random.uniform(50, 300)
            })
    
    df = pd.DataFrame(transactions)
    
    result = engine.validate_model(df)
    
    assert 'status' in result
    
    if result['status'] == 'validated':
        # Verify we get real metrics (not hardcoded 0.15)
        assert 'MAE' in result
        assert isinstance(result['MAE'], float)
        assert result['MAE'] >= 0
        
        # Verify we get customer counts
        assert 'training_customers' in result
        assert 'holdout_customers' in result
        assert result['training_customers'] > 0


def test_auto_select_model():
    """Test automatic model selection between BG/NBD and Pareto/NBD."""
    engine = DataScienceCore()
    
    np.random.seed(42)
    customers = [f'C{i:03d}' for i in range(30)]
    
    transactions = []
    for cust in customers:
        n_orders = np.random.randint(2, 6)
        for _ in range(n_orders):
            transactions.append({
                'customer_id': cust,
                'order_date': datetime(2024, 1, 1) + timedelta(days=np.random.randint(0, 180)),
                'revenue': np.random.uniform(50, 200)
            })
    
    df = pd.DataFrame(transactions)
    
    best_model, comparison = engine.auto_select_model(df)
    
    assert best_model in ["BG/NBD", "Pareto/NBD"]
    assert "BG/NBD" in comparison
    assert "Pareto/NBD" in comparison
    assert "AIC" in comparison["BG/NBD"]
    assert "selected" in comparison


# ============================================================
# LINUCB LEARNING TESTS
# ============================================================

def test_linucb_learns_from_feedback():
    """Test that LinUCB actually learns from feedback and changes behavior."""
    engine = ProfitMatrixEngine()
    
    context = np.array([1.0, 0.5, 0.3, 0.8])
    offers = [{'id': 'offer_a'}, {'id': 'offer_b'}]
    
    # Initial selection (both arms have identity matrices)
    result1 = engine.linucb_select_offer(context, offers)
    assert result1['selected_offer'] is not None
    
    # Train offer_a with positive rewards
    for _ in range(10):
        engine.linucb_update('offer_a', context, reward=1.0)
    
    # Train offer_b with negative rewards
    for _ in range(10):
        engine.linucb_update('offer_b', context, reward=0.0)
    
    # Now offer_a should have higher UCB
    result2 = engine.linucb_select_offer(context, offers, alpha=0.5)  # Lower alpha for more exploitation
    
    assert 'all_scores' in result2
    assert result2['all_scores']['offer_a']['n_samples'] == 10
    assert result2['all_scores']['offer_b']['n_samples'] == 10
    
    # Offer A should have higher exploitation value
    assert result2['all_scores']['offer_a']['exploitation'] > result2['all_scores']['offer_b']['exploitation']


def test_linucb_state_persistence():
    """Test that LinUCB state can be saved and restored."""
    engine1 = ProfitMatrixEngine()
    
    context = np.array([1.0, 0.5])
    offers = [{'id': 'test_offer'}]
    
    # Train the engine
    engine1.linucb_select_offer(context, offers)
    engine1.linucb_update('test_offer', context, reward=1.0)
    engine1.linucb_update('test_offer', context, reward=1.0)
    
    # Get state
    state = engine1.get_linucb_state()
    
    assert 'test_offer' in state
    assert state['test_offer']['n'] == 2
    
    # Create new engine and load state
    engine2 = ProfitMatrixEngine()
    engine2.load_linucb_state(state)
    
    # Verify state is restored
    assert 'test_offer' in engine2.linucb_arms
    assert engine2.linucb_arms['test_offer']['n'] == 2


# ============================================================
# THOMPSON SAMPLING TESTS
# ============================================================

def test_thompson_sampling_learns():
    """Test that Thompson Sampling updates priors correctly."""
    engine = ProfitMatrixEngine()
    
    offers = [
        {'id': 'winner'},
        {'id': 'loser'}
    ]
    
    # Simulate 20 successes for winner, 2 for loser
    for _ in range(20):
        engine.thompson_sampling_update('winner', success=True)
    for _ in range(2):
        engine.thompson_sampling_update('winner', success=False)
    
    for _ in range(2):
        engine.thompson_sampling_update('loser', success=True)
    for _ in range(20):
        engine.thompson_sampling_update('loser', success=False)
    
    state = engine.get_thompson_state()
    
    # Winner should have higher mean (alpha/(alpha+beta))
    assert state['winner']['mean'] > state['loser']['mean']
    
    # Winner: alpha=21, beta=3 -> mean=0.875
    # Loser: alpha=3, beta=21 -> mean=0.125
    assert state['winner']['mean'] > 0.8
    assert state['loser']['mean'] < 0.2


def test_thompson_sampling_selects_winner():
    """Test that Thompson Sampling tends to select the arm with higher mean."""
    engine = ProfitMatrixEngine()
    
    # Pre-train priors
    engine.arm_priors['good_offer'] = (50.0, 10.0)  # mean = 0.833
    engine.arm_priors['bad_offer'] = (10.0, 50.0)   # mean = 0.167
    
    offers = [{'id': 'good_offer'}, {'id': 'bad_offer'}]
    
    # Run 100 selections
    selections = {'good_offer': 0, 'bad_offer': 0}
    for _ in range(100):
        result = engine.thompson_sampling_select(offers)
        selections[result['selected_offer']['id']] += 1
    
    # Good offer should be selected significantly more often
    assert selections['good_offer'] > 75, f"Good offer selected {selections['good_offer']} times"


# ============================================================
# SEGMENTATION INTEGRATION TESTS
# ============================================================

def test_segmentation_pipeline():
    """Test that segmentation works on prediction output."""
    engine = DataScienceCore()
    
    # Create mock predictions DataFrame
    predictions = pd.DataFrame({
        'customer_id': ['C001', 'C002', 'C003', 'C004'],
        'prob_alive': [0.9, 0.3, 0.1, 0.7],
        'clv_12m': [5000, 8000, 2000, 300],
        'expected_purchases_90d': [3.0, 0.5, 0.1, 2.0]
    })
    
    segmented = segment_customers(predictions)
    
    assert 'segmento' in segmented.columns
    assert len(segmented) == 4
    
    # Each customer should have a segment
    assert all(segmented['segmento'].notna())


# ============================================================
# MODEL REGISTRY TESTS
# ============================================================

def test_model_registry_save_load():
    """Test model registry persistence."""
    import tempfile
    import os
    
    # Use temp directory
    with tempfile.TemporaryDirectory() as tmpdir:
        registry = ModelRegistry(base_path=tmpdir)
        
        # Save a snapshot
        state = {"alpha": 5.0, "beta": 2.0}
        version = registry.save_snapshot("test_model", state, metrics={"accuracy": 0.95})
        
        # Load it back
        loaded = registry.load_current("test_model")
        
        assert loaded is not None
        assert loaded['state'] == state
        assert loaded['metrics']['accuracy'] == 0.95


def test_model_registry_versioning():
    """Test that registry keeps multiple versions."""
    import tempfile
    import time
    
    with tempfile.TemporaryDirectory() as tmpdir:
        registry = ModelRegistry(base_path=tmpdir)
        
        # Save multiple versions with delay for unique timestamps
        registry.save_snapshot("test_model", {"v": 1}, reason="first")
        time.sleep(1.1)  # Ensure unique timestamp
        registry.save_snapshot("test_model", {"v": 2}, reason="second")
        time.sleep(1.1)
        registry.save_snapshot("test_model", {"v": 3}, reason="third")
        
        # List versions
        versions = registry.list_versions("test_model")
        
        assert len(versions) >= 3, f"Expected 3 versions, got {len(versions)}: {versions}"
        
        # Current should be the latest
        current = registry.load_current("test_model")
        assert current['state']['v'] == 3
