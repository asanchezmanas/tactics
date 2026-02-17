"""
Explainer Registry

Central registry for all algorithm explainers.
Allows adding new explainers without modifying core code.
"""

from typing import Dict, Optional, Type
from .base import ExplainerBase
import logging

logger = logging.getLogger("tactics.core.explainers")


class ExplainerRegistry:
    """
    Singleton registry for algorithm explainers.
    
    Usage:
        # Register an explainer
        ExplainerRegistry.register("ltv", LTVExplainer())
        
        # Get an explainer
        explainer = ExplainerRegistry.get("ltv")
        result = explainer.explain("clv", 487.32, context)
    """
    
    _instance: Optional["ExplainerRegistry"] = None
    _explainers: Dict[str, ExplainerBase] = {}
    
    def __new__(cls) -> "ExplainerRegistry":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._bootstrap()
        return cls._instance
    
    def _bootstrap(self) -> None:
        """Auto-registers core explainers."""
        try:
            from .ltv_explainer import LTVExplainer
            from .mmm_explainer import MMMExplainer
            from .eclat_explainer import ECLATExplainer
            from .bandit_explainer import ThompsonExplainer, LinUCBExplainer
            from .profit_explainer import ProfitExplainer
            from .integrity_explainer import IntegrityExplainer
            
            self.register("ltv", LTVExplainer())
            self.register("mmm", MMMExplainer())
            self.register("eclat", ECLATExplainer())
            self.register("thompson", ThompsonExplainer())
            self.register("linucb", LinUCBExplainer())
            self.register("profit", ProfitExplainer())
            self.register("integrity", IntegrityExplainer())
        except Exception as e:
            logger.error(f"ExplainerRegistry bootstrap failed: {e}")
            # Do not re-raise to allow the rest of the app to function, 
            # but log the failure clearly.

    @classmethod
    def register(cls, category: str, explainer: ExplainerBase) -> None:
        """
        Register an explainer for a category.
        
        Args:
            category: Algorithm category (e.g., "ltv", "mmm")
            explainer: Instance of ExplainerBase subclass
        """
        cls._explainers[category] = explainer
    
    @classmethod
    def get(cls, category: str) -> Optional[ExplainerBase]:
        if cls._instance is None:
            cls()
        return cls._explainers.get(category)
    
    @classmethod
    def get_all(cls) -> Dict[str, ExplainerBase]:
        """Get all registered explainers."""
        return cls._explainers.copy()
    
    @classmethod
    def list_categories(cls) -> list:
        if cls._instance is None:
            cls()
        return list(cls._explainers.keys())
    
    @classmethod
    def list_all_metrics(cls) -> Dict[str, list]:
        """List all metrics by category."""
        return {
            category: explainer.get_supported_metrics()
            for category, explainer in cls._explainers.items()
        }
    
    @classmethod
    def explain(cls, category: str, metric_id: str, value, context=None):
        """
        Convenience method to explain a metric directly.
        
        Args:
            category: Algorithm category
            metric_id: Metric identifier
            value: Metric value
            context: Optional context dict
            
        Returns:
            ExplainedResult or None if category not found
        """
        explainer = cls.get(category)
        if explainer:
            return explainer.explain(metric_id, value, context)
        return None
    
    @classmethod
    def clear(cls) -> None:
        """Clear all registered explainers. Useful for testing."""
        cls._explainers.clear()


# Convenience function
def explain(category: str, metric_id: str, value, context=None):
    """
    Top-level convenience function for explaining metrics.
    
    Usage:
        from core.explainers import explain
        result = explain("ltv", "clv", 487.32)
    """
    return ExplainerRegistry.explain(category, metric_id, value, context)
