"""
Unit Tests for Enterprise SOTA Engines

Tests for:
- engine_enterprise.py (LSTM LTV)
- optimizer_enterprise.py (Bayesian MMM)
"""

import pytest
import numpy as np
import pandas as pd
from datetime import datetime, timedelta


# ============================================================
# FIXTURES
# ============================================================

@pytest.fixture
def sample_transactions():
    """Generate sample transaction data for testing."""
    np.random.seed(42)
    n_customers = 100
    n_transactions = 500
    
    data = {
        'customer_id': np.random.choice(range(1, n_customers + 1), n_transactions),
        'order_date': [
            datetime(2024, 1, 1) + timedelta(days=np.random.randint(0, 365))
            for _ in range(n_transactions)
        ],
        'revenue': np.random.exponential(50, n_transactions) + 10
    }
    return pd.DataFrame(data)


@pytest.fixture
def sample_spend_data():
    """Generate sample marketing spend data for MMM testing."""
    np.random.seed(42)
    n_periods = 52  # Weekly data
    
    data = {
        'Meta Ads': np.random.uniform(1000, 5000, n_periods),
        'Google Ads': np.random.uniform(2000, 8000, n_periods),
        'TikTok Ads': np.random.uniform(500, 2000, n_periods)
    }
    return pd.DataFrame(data)


@pytest.fixture
def sample_revenue():
    """Generate sample revenue data correlated with spend."""
    np.random.seed(42)
    n_periods = 52
    
    base_revenue = 50000
    noise = np.random.normal(0, 5000, n_periods)
    trend = np.linspace(0, 10000, n_periods)
    
    return base_revenue + trend + noise


# ============================================================
# ENGINE ENTERPRISE TESTS
# ============================================================

class TestEnterpriseDataScienceCore:
    """Tests for LSTM-based LTV prediction engine."""
    
    def test_import(self):
        """Test that the module imports correctly."""
        from core.engine_enterprise import EnterpriseDataScienceCore
        engine = EnterpriseDataScienceCore()
        assert engine is not None
        assert engine.model_type == 'LSTM'
    
    def test_sequence_preparation(self, sample_transactions):
        """Test sequence data preparation for LSTM."""
        from core.engine_enterprise import EnterpriseDataScienceCore
        
        engine = EnterpriseDataScienceCore(sequence_length=6)
        X, y, customer_ids = engine.prepare_sequence_data(sample_transactions)
        
        # Check shapes
        assert len(X.shape) == 3  # (customers, sequence_length, features)
        assert X.shape[1] == 6  # sequence_length
        assert X.shape[2] == 4  # features
        assert len(y) == len(customer_ids)
        assert len(y) > 0
    
    def test_baseline_distribution(self):
        """Test baseline distribution setting for drift detection."""
        from core.engine_enterprise import EnterpriseDataScienceCore
        
        engine = EnterpriseDataScienceCore()
        ltv_values = np.random.exponential(100, 1000)
        
        engine.set_baseline_distribution(ltv_values)
        
        assert engine.baseline_distribution is not None
        assert 'mean' in engine.baseline_distribution
        assert 'histogram' in engine.baseline_distribution
    
    def test_drift_detection_no_drift(self):
        """Test drift detection with similar distribution."""
        from core.engine_enterprise import EnterpriseDataScienceCore
        
        engine = EnterpriseDataScienceCore()
        
        # Set baseline
        baseline_ltv = np.random.exponential(100, 1000)
        engine.set_baseline_distribution(baseline_ltv)
        
        # Test with similar distribution
        new_ltv = np.random.exponential(100, 500)
        result = engine.detect_cohort_drift(new_ltv)
        
        assert 'is_drifting' in result
        assert 'kl_divergence' in result
        assert 'js_divergence' in result
    
    def test_drift_detection_with_drift(self):
        """Test drift detection with significantly different distribution."""
        from core.engine_enterprise import EnterpriseDataScienceCore
        
        engine = EnterpriseDataScienceCore()
        engine.drift_threshold = 0.1  # Lower threshold for easier detection
        
        # Set baseline with low values
        baseline_ltv = np.random.exponential(50, 1000)
        engine.set_baseline_distribution(baseline_ltv)
        
        # Test with much higher values (drift)
        new_ltv = np.random.exponential(200, 500)
        result = engine.detect_cohort_drift(new_ltv)
        
        assert result['is_drifting'] == True
        assert result['mean_shift_pct'] > 50  # Significant shift
    
    def test_feature_expansion(self):
        """Test multi-source feature expansion."""
        from core.engine_enterprise import EnterpriseDataScienceCore
        
        engine = EnterpriseDataScienceCore()
        
        rfm_df = pd.DataFrame({
            'customer_id': [1, 2, 3],
            'recency': [10, 20, 30],
            'frequency': [5, 3, 1],
            'monetary': [500, 300, 100]
        })
        
        web_engagement = pd.DataFrame({
            'customer_id': [1, 2],
            'page_views': [50, 30]
        })
        
        expanded = engine.expand_features(rfm_df, web_engagement=web_engagement)
        
        assert 'page_views' in expanded.columns
        assert len(expanded) == 3  # All RFM customers
        assert expanded.loc[expanded['customer_id'] == 3, 'page_views'].values[0] == 0


# ============================================================
# OPTIMIZER ENTERPRISE TESTS
# ============================================================

class TestEnterpriseMMOptimizer:
    """Tests for Bayesian MMM optimizer."""
    
    def test_import(self):
        """Test that the module imports correctly."""
        from core.optimizer_enterprise import EnterpriseMMOptimizer
        optimizer = EnterpriseMMOptimizer()
        assert optimizer is not None
    
    def test_geometric_adstock(self):
        """Test geometric adstock transformation."""
        from core.optimizer_enterprise import EnterpriseMMOptimizer
        
        x = np.array([100, 0, 0, 0, 0])
        result = EnterpriseMMOptimizer.geometric_adstock(x, decay=0.5)
        
        assert result[0] == 100
        assert result[1] == 50  # 0 + 0.5 * 100
        assert result[2] == 25  # 0 + 0.5 * 50
        assert result[3] == 12.5
    
    def test_weibull_adstock(self):
        """Test Weibull adstock transformation."""
        from core.optimizer_enterprise import EnterpriseMMOptimizer
        
        x = np.array([100, 50, 75, 25, 0])
        result = EnterpriseMMOptimizer.weibull_adstock(x, shape=2.0, scale=3.0)
        
        assert len(result) == len(x)
        assert not np.isnan(result).any()
    
    def test_hill_saturation(self):
        """Test Hill saturation function."""
        from core.optimizer_enterprise import EnterpriseMMOptimizer
        
        x = np.array([0, 50, 100, 500, 1000])
        result = EnterpriseMMOptimizer.hill_saturation(x, alpha=2.0, gamma=100)
        
        assert result[0] == 0  # Zero input = zero output
        assert 0 < result[1] < result[2] < result[3] < result[4]  # Increasing
        assert result[-1] < 1  # Below saturation max
    
    def test_channel_synergy(self):
        """Test channel synergy matrix."""
        from core.optimizer_enterprise import EnterpriseMMOptimizer
        
        optimizer = EnterpriseMMOptimizer()
        channels = ['Meta', 'Google', 'TikTok']
        synergy = {('Meta', 'Google'): 1.15}
        
        matrix = optimizer.set_channel_synergy(channels, synergy)
        
        assert matrix.shape == (3, 3)
        assert matrix[0, 1] == 1.15  # Meta-Google synergy
        assert matrix[1, 0] == 1.15  # Symmetric
        assert matrix[0, 0] == 1.0  # Diagonal = 1
    
    def test_fallback_inference(self, sample_spend_data, sample_revenue):
        """Test bootstrap fallback when PyMC is unavailable."""
        from core.optimizer_enterprise import EnterpriseMMOptimizer
        
        optimizer = EnterpriseMMOptimizer()
        
        result = optimizer._fallback_inference(
            sample_spend_data.values,
            np.array(sample_revenue),
            sample_spend_data.columns.tolist()
        )
        
        assert 'posterior_means' in result
        assert 'credibility_intervals_90' in result
        assert len(result['posterior_means']) == 3
        assert result['model_type'] == 'bootstrap_ridge_fallback'
    
    def test_scipy_hyperparameter_tuning(self, sample_spend_data, sample_revenue):
        """Test hyperparameter tuning with scipy fallback."""
        from core.optimizer_enterprise import EnterpriseMMOptimizer
        
        optimizer = EnterpriseMMOptimizer()
        
        result = optimizer._tune_with_scipy(
            sample_spend_data.values,
            np.array(sample_revenue),
            param_bounds={
                "decay": (0.1, 0.9),
                "hill_alpha": (0.5, 3.0),
                "hill_gamma": (0.1, 2.0)
            },
            n_channels=3
        )
        
        assert 'decay' in result
        assert 'hill_alpha' in result
        assert 'hill_gamma' in result
        assert 'final_r2' in result
        assert len(result['decay']) == 3
    
    def test_budget_optimization(self):
        """Test budget allocation optimization."""
        from core.optimizer_enterprise import EnterpriseMMOptimizer
        
        optimizer = EnterpriseMMOptimizer()
        optimizer.fitted_params = {
            'hill_alpha': [1.5, 1.5, 1.5],
            'hill_gamma': [0.5, 0.5, 0.5]
        }
        
        result = optimizer.optimize_budget(
            total_budget=10000,
            channel_coefficients=[0.5, 0.3, 0.2]
        )
        
        assert 'optimal_allocation' in result
        assert sum(result['optimal_allocation']) == pytest.approx(10000, rel=0.01)
        assert 'marginal_roas' in result


# ============================================================
# INTEGRATION TESTS
# ============================================================

class TestEnterpriseIntegration:
    """Integration tests for the full enterprise pipeline."""
    
    def test_full_ltv_pipeline(self, sample_transactions):
        """Test full LTV prediction pipeline (fallback mode)."""
        from core.engine_enterprise import run_enterprise_ltv_pipeline
        
        result = run_enterprise_ltv_pipeline(
            sample_transactions,
            sequence_length=6,
            epochs=5  # Few epochs for speed
        )
        
        assert 'predictions' in result
        assert 'training_metrics' in result
        assert len(result['predictions']) > 0
    
    def test_full_mmm_pipeline(self, sample_spend_data, sample_revenue):
        """Test full MMM optimization pipeline."""
        from core.optimizer_enterprise import run_enterprise_mmm_pipeline
        
        result = run_enterprise_mmm_pipeline(
            spend_df=sample_spend_data,
            revenue_series=pd.Series(sample_revenue),
            total_budget=15000,
            synergy_config={('Meta Ads', 'Google Ads'): 1.1}
        )
        
        assert 'optimal_allocation' in result
        assert 'tuned_parameters' in result
        assert result['tier'] == 'enterprise'


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
