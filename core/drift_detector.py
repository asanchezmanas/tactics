"""
Drift Detector: Conservative Model Health Monitoring.

Philosophy:
- Only flag drift when it's SIGNIFICANT
- Err on the side of NOT retraining
- Simple heuristics, not complex ML
"""
import numpy as np
from typing import Dict, Optional, List
from datetime import datetime, timedelta


class DriftDetector:
    """
    Detects when models need retraining using simple, conservative heuristics.
    """
    
    # Minimum days between retraining (cooldown)
    RETRAIN_COOLDOWN_DAYS = 7
    
    def __init__(self):
        self.last_retrain: Dict[str, datetime] = {}
    
    def check_eclat_drift(
        self, 
        current_basket_size: float,
        historical_basket_size: float,
        current_top_bundle_support: float,
        historical_top_bundle_support: float
    ) -> Dict:
        """
        Check if ECLAT model needs retraining.
        
        Drift signals:
        1. Average basket size changed by >25% (purchase behavior shift)
        2. Top bundle support dropped by >40% (product popularity shift)
        """
        basket_change = abs(current_basket_size - historical_basket_size) / max(historical_basket_size, 0.01)
        support_change = (historical_top_bundle_support - current_top_bundle_support) / max(historical_top_bundle_support, 0.01)
        
        drift_detected = basket_change > 0.25 or support_change > 0.40
        
        return {
            "model": "eclat",
            "drift_detected": drift_detected,
            "basket_size_change": round(basket_change * 100, 1),
            "support_drop": round(support_change * 100, 1),
            "threshold_basket": 25,
            "threshold_support": 40,
            "recommendation": "retrain" if drift_detected else "skip"
        }
    
    def check_thompson_staleness(
        self,
        arm_priors: Dict[str, Dict],
        min_observations: int = 100
    ) -> Dict:
        """
        Check if Thompson Sampling priors are stale.
        
        Staleness signals:
        1. Total observations > threshold AND variance is very low (converged)
        2. All arms have similar means (no learning happening)
        """
        if not arm_priors:
            return {"model": "thompson", "drift_detected": False, "reason": "no_data"}
        
        total_obs = sum(p.get('alpha', 1) + p.get('beta', 1) - 2 for p in arm_priors.values())
        means = [p.get('mean', 0.5) for p in arm_priors.values()]
        
        # Check if converged (low variance in means)
        mean_variance = np.var(means) if len(means) > 1 else 0
        converged = total_obs > min_observations and mean_variance < 0.01
        
        return {
            "model": "thompson",
            "drift_detected": converged,
            "total_observations": int(total_obs),
            "mean_variance": round(mean_variance, 4),
            "recommendation": "decay_priors" if converged else "continue"
        }
    
    def check_ltv_drift(
        self,
        current_recency_median: float,
        historical_recency_median: float,
        current_frequency_mean: float,
        historical_frequency_mean: float
    ) -> Dict:
        """
        Check if LTV/Churn model needs retraining.
        
        Drift signals:
        1. Median recency changed by >30% (customer behavior shift)
        2. Mean frequency changed by >25%
        """
        recency_change = abs(current_recency_median - historical_recency_median) / max(historical_recency_median, 0.01)
        frequency_change = abs(current_frequency_mean - historical_frequency_mean) / max(historical_frequency_mean, 0.01)
        
        drift_detected = recency_change > 0.30 or frequency_change > 0.25
        
        return {
            "model": "ltv_churn",
            "drift_detected": drift_detected,
            "recency_change": round(recency_change * 100, 1),
            "frequency_change": round(frequency_change * 100, 1),
            "recommendation": "retrain" if drift_detected else "skip"
        }
    
    def check_cooldown(self, model_name: str) -> bool:
        """Check if model is still in cooldown period after last retrain."""
        last = self.last_retrain.get(model_name)
        if last is None:
            return False
        
        cooldown_end = last + timedelta(days=self.RETRAIN_COOLDOWN_DAYS)
        return datetime.utcnow() < cooldown_end
    
    def record_retrain(self, model_name: str):
        """Record that a model was retrained."""
        self.last_retrain[model_name] = datetime.utcnow()


def calculate_thompson_decay(
    arm_priors: Dict[str, Dict],
    decay_factor: float = 0.9,
    min_sum: float = 2.0
) -> Dict[str, Dict]:
    """
    Apply decay to Thompson Sampling priors.
    
    Purpose: Prevent old data from dominating, allow adaptation to new trends.
    
    Args:
        arm_priors: Current priors {id: {alpha, beta, mean}}
        decay_factor: Multiply alpha and beta by this (default 0.9)
        min_sum: Never let alpha + beta go below this (revert to uniform)
    
    Returns:
        Updated priors
    """
    decayed = {}
    for arm_id, prior in arm_priors.items():
        alpha = prior.get('alpha', 1.0) * decay_factor
        beta = prior.get('beta', 1.0) * decay_factor
        
        # Enforce minimum to prevent near-zero priors
        if alpha + beta < min_sum:
            alpha = 1.0
            beta = 1.0
        
        decayed[arm_id] = {
            "alpha": round(alpha, 2),
            "beta": round(beta, 2),
            "mean": round(alpha / (alpha + beta), 4)
        }
    
    return decayed
