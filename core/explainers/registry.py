"""
Explainer Registry

Central registry for all algorithm explainers.
Allows adding new explainers without modifying core code.
"""

from typing import Dict, Optional, Type
from .base import ExplainerBase


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
        return cls._instance
    
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
        """
        Get the explainer for a category.
        
        Args:
            category: Algorithm category
            
        Returns:
            ExplainerBase instance or None if not registered
        """
        return cls._explainers.get(category)
    
    @classmethod
    def get_all(cls) -> Dict[str, ExplainerBase]:
        """Get all registered explainers."""
        return cls._explainers.copy()
    
    @classmethod
    def list_categories(cls) -> list:
        """List all registered categories."""
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
