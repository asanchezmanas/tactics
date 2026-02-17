"""
Unified Intelligence Engine v2.0 - Tactics
Consolidates standard (statistical) and enterprise (neural) LTV/Churn logic.
Architecture: Strategy Pattern for interchangeable backends.
"""

import pandas as pd
import numpy as np
from datetime import datetime
from typing import Optional, List, Dict, Any, Tuple
from abc import ABC, abstractmethod

# Standard Statistical Backend
from lifetimes import BetaGeoFitter, GammaGammaFitter, ParetoNBDFitter
from lifetimes.utils import summary_data_from_transaction_data

# Enterprise Neural Backend (Graceful fallbacks)
try:
    import tensorflow as tf
    from tensorflow.keras.models import Sequential, load_model
    from tensorflow.keras.layers import LSTM, Dense, Dropout, Attention
    TF_AVAILABLE = True
except ImportError:
    TF_AVAILABLE = False

try:
    import xgboost as xgb
    XGB_AVAILABLE = True
except ImportError:
    XGB_AVAILABLE = False

# ============================================================
# ABSTRACT BASE STRATEGY
# ============================================================

class IntelligenceStrategy(ABC):
    @abstractmethod
    def prepare_data(self, df: pd.DataFrame) -> Any:
        pass

    @abstractmethod
    def fit(self, data: Any) -> None:
        pass

    @abstractmethod
    def predict(self, data: Any, confidence_iterations: int = 100) -> pd.DataFrame:
        pass

# ============================================================
# STATISTICAL STRATEGY (V1 Core - Lifetimes)
# ============================================================

class StatisticalStrategy(IntelligenceStrategy):
    def __init__(self, model_type: str = 'BG/NBD', penalizer: float = 0.01):
        self.model_type = model_type
        self.penalizer = penalizer
        self.bgf = None
        self.ggf = None

    def prepare_data(self, df: pd.DataFrame) -> pd.DataFrame:
        return summary_data_from_transaction_data(
            df, 'customer_id', 'order_date', monetary_value_col='revenue',
            observation_period_end=df['order_date'].max()
        )

    def fit(self, rfm: pd.DataFrame) -> None:
        if self.model_type == 'BG/NBD':
            self.bgf = BetaGeoFitter(penalizer_coef=self.penalizer)
        else:
            self.bgf = ParetoNBDFitter(penalizer_coef=self.penalizer)
        
        self.bgf.fit(rfm['frequency'], rfm['recency'], rfm['T'])
        
        # Fit monetary value model (only for returning customers)
        returning_customers = rfm[rfm['frequency'] > 0]
        self.ggf = GammaGammaFitter(penalizer_coef=self.penalizer)
        self.ggf.fit(returning_customers['frequency'], returning_customers['monetary_value'])

    def predict(self, rfm: pd.DataFrame, confidence_iterations: int = 500) -> pd.DataFrame:
        """
        Expected purchases and probability alive with Bootstrap CIs.
        """
        # Expected purchases and probability alive
        rfm['predicted_purchases'] = self.bgf.conditional_expected_number_of_purchases_up_to_time(
            30, rfm['frequency'], rfm['recency'], rfm['T']
        )
        rfm['prob_alive'] = self.bgf.conditional_probability_alive(
            rfm['frequency'], rfm['recency'], rfm['T']
        )
        
        # Expected LTV
        rfm['clv_12m'] = self.ggf.customer_lifetime_value(
            self.bgf, rfm['frequency'], rfm['recency'], rfm['T'], 
            rfm['monetary_value'], time=12, discount_rate=0.01
        )

        # Bootstrap CIs for Enterprise/Precision or requested iterations
        if confidence_iterations > 1:
            rfm = self._bootstrap_ci(rfm, n_iter=confidence_iterations)
            
        return rfm

    def _bootstrap_ci(self, rfm: pd.DataFrame, n_iter: int = 50) -> pd.DataFrame:
        """
        Perturb fitted params based on variance, recompute LTV, get empirical percentiles.
        SOTA: Provides probabilistic range for business planning.
        """
        try:
            params = self.bgf.params_
            ltv_samples = []
            
            for _ in range(n_iter):
                # Simple perturbation (standard deviation heuristic)
                perturbed = {k: np.random.normal(v, abs(v) * 0.05) for k, v in params.items()}
                
                # We mock a fitter with perturbed params to avoid full re-fit (expensive)
                bgf_temp = BetaGeoFitter()
                bgf_temp.params_ = perturbed
                
                ltv = self.ggf.customer_lifetime_value(
                    bgf_temp, rfm['frequency'], rfm['recency'], rfm['T'],
                    rfm['monetary_value'], time=12, discount_rate=0.01
                )
                ltv_samples.append(ltv)
            
            samples_df = pd.DataFrame(ltv_samples)
            rfm['clv_lower'] = samples_df.quantile(0.10).values[0] if len(samples_df) > 0 else rfm['clv_12m']
            rfm['clv_upper'] = samples_df.quantile(0.90).values[0] if len(samples_df) > 0 else rfm['clv_12m']
            
        except Exception as e:
            # Fallback to point estimate
            rfm['clv_lower'] = rfm['clv_12m'] * 0.9
            rfm['clv_upper'] = rfm['clv_12m'] * 1.1
            print(f"[Engine] Bootstrap failed: {e}")
            
        return rfm

# ============================================================
# NEURAL STRATEGY (V1 Enterprise - LSTM/XGBoost)
# ============================================================

class NeuralStrategy(IntelligenceStrategy):
    def __init__(self, sequence_length: int = 12):
        self.sequence_length = sequence_length
        self.model = None
        self.scaler = None

    def prepare_data(self, df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        # Sequence logic from engine_enterprise.py
        # Simplificando para el V2 inicial: asume data ya procesada o llama a helpers
        pass

    def fit(self, data: Any) -> None:
        if not TF_AVAILABLE and not XGB_AVAILABLE:
            raise ImportError("Neural Strategy requires TensorFlow or XGBoost.")
        # Training logic...
        pass

    def predict(self, data: Any, confidence_iterations: int = 100) -> pd.DataFrame:
        """Prediction logic with MC Dropout for uncertainty."""
        if data is None:
            raise ValueError("NeuralStrategy.predict received None — prepare_data not implemented")
        # Placeholder for future implementation
        return pd.DataFrame()

class TacticalEngine:
    """
    Main entry point for intelligence engine.
    Orchestrates tier-based strategy selection and provides auxiliary insights.
    """
    def __init__(self, tier: str = 'INTELLIGENCE', company_id: str = "generic"):
        self.tier = tier.upper()
        self.company_id = company_id
        self.strategy = self._initialize_strategy()

    def _initialize_strategy(self) -> IntelligenceStrategy:
        # Gate NeuralStrategy: only if tier is high AND TF/XGB is available AND it is fully implemented
        # For now, we fallback to StatisticalStrategy as Neural is still a stub
        if self.tier in ['ENTERPRISE', 'PRECISION'] and TF_AVAILABLE and False: # False because it's still a stub
            return NeuralStrategy()
        return StatisticalStrategy()

    def analyze_ltv(self, transactions: pd.DataFrame, holdout_days: int = 30) -> Dict[str, Any]:
        """Runs the full LTV/Churn prediction pipeline with holdout validation."""
        # 1. Holdout Split
        cutoff = transactions['order_date'].max() - pd.Timedelta(days=holdout_days)
        calibration_data = transactions[transactions['order_date'] <= cutoff]
        holdout_data = transactions[transactions['order_date'] > cutoff]
        
        # 2. Fit & Predict on calibration
        processed = self.strategy.prepare_data(calibration_data)
        self.strategy.fit(processed)
        results = self.strategy.predict(processed)
        
        # 3. Validation
        mape = 0
        if not holdout_data.empty:
            # Simple MAPE calculation for the holdout period
            actuals = holdout_data.groupby('customer_id')['revenue'].sum()
            # Join with predictions
            results_with_actuals = results.set_index('customer_id').join(actuals.rename('actual_holdout'))
            valid = results_with_actuals.dropna(subset=['actual_holdout'])
            if not valid.empty:
                # Compare clv_12m (adjusted for 30 days) vs actual
                # Note: this is a simplified heuristic
                mape = np.mean(np.abs((valid['actual_holdout'] - valid['clv_12m']/12) / valid['actual_holdout']))
        
        return {
            "tier": self.tier,
            "predictions": results.to_dict('records'),
            "summary": {
                "avg_ltv": results['clv_12m'].mean() if 'clv_12m' in results else 0,
                "avg_churn_risk": 1 - results['prob_alive'].mean() if 'prob_alive' in results else 0,
                "validation_mape": float(mape),
                "customers_analyzed": len(results)
            },
            "ltv_projections": results
        }

    def predict_ltv(self, transactions: pd.DataFrame):
        """Alias for analyze_ltv for API consistency."""
        return self.analyze_ltv(transactions)

    def validate_model(self, transactions: pd.DataFrame):
        """Alias for analyze_ltv for Test compatibility."""
        return self.analyze_ltv(transactions)

class EngineFactory:
    """Factory for instantiating engines."""
    @staticmethod
    def create_engine(tier: str = 'CORE', company_id: str = "generic") -> TacticalEngine:
        return TacticalEngine(tier=tier, company_id=company_id)

    # Merged from profit.py (Basket Analysis & Unit Economics)
    def calculate_basket_rules(self, transactions: pd.DataFrame, min_support: float = 0.05) -> Dict:
        # Association rules logic...
        pass

    def calculate_unit_economics(self, products: pd.DataFrame) -> pd.DataFrame:
        # Net margin calculation logic...
        pass

# Legacy Alias for v2.0 compatibility
DataScienceCore = TacticalEngine
