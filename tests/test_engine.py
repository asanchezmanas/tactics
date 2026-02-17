import unittest
import pandas as pd
import numpy as np
from core.engine import TacticalEngine, EngineFactory
from core.optimizer import MarketingOptimizer
from core.integrity import UnifiedIntegrityGuard

class TestTacticsV2(unittest.TestCase):
    def setUp(self):
        # Sample Data for Testing (Transaction Level)
        # 500 transactions for 50 customers to ensure some repeat business
        self.sample_df = pd.DataFrame({
            'customer_id': np.random.randint(0, 50, 500),
            'revenue': np.random.uniform(10, 500, 500),
            'order_date': pd.to_datetime('2023-01-01') + pd.to_timedelta(np.random.randint(0, 365, 500), unit='D')
        })

    def test_engine_factory_standard(self):
        """Verify factory returns correct strategy for CORE tier."""
        engine = EngineFactory.create_engine(tier='CORE')
        self.assertEqual(engine.tier, 'CORE')
        # Check if predict method exists and runs
        res = engine.predict_ltv(self.sample_df)
        self.assertIn('ltv_projections', res)

    def test_engine_factory_enterprise(self):
        """Verify factory returns correct strategy for ENTERPRISE tier."""
        engine = EngineFactory.create_engine(tier='ENTERPRISE')
        self.assertEqual(engine.tier, 'ENTERPRISE')
        try:
            res = engine.predict_ltv(self.sample_df)
            self.assertIn('ltv_projections', res)
        except ImportError:
            # Expected if TF/XGB are not installed
            print("Skipping NeuralStrategy fit test due to missing dependencies.")
            self.assertTrue(True)

    def test_optimizer_fit(self):
        """Verify MarketingOptimizer can fit response curves."""
        optimizer = MarketingOptimizer(tier='CORE')
        spend = pd.DataFrame({'FB': [100, 200, 300], 'Google': [150, 250, 350]})
        revenue = pd.Series([1000, 2000, 3000])
        optimizer.fit_response_curves(spend, revenue)
        self.assertIsNotNone(optimizer.channel_models)

    def test_integrity_guard(self):
        """Verify the consolidated integrity guard catches empty data."""
        guard = UnifiedIntegrityGuard()
        issues = guard.validate_ingestion(pd.DataFrame(), source_type='shopify')
        self.assertTrue(any(issue.severity == 'critical' for issue in issues))

    def test_simulation_integration(self):
        """Sanity check for the unified simulation entry point."""
        # This just verifies imports and class instantiation in a 'sim-like' flow
        engine = TacticalEngine(tier='CORE')
        self.assertTrue(hasattr(engine, 'strategy'))

if __name__ == '__main__':
    unittest.main()
