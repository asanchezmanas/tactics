"""
Explainer Engine - SOTA System for Plain Language Metric Explanations

This package provides a robust, extensible system for translating
algorithm outputs into honest, understandable explanations for
non-technical users.

Principles:
1. Honesty - Never sound certain when there's uncertainty
2. Clarity - 6th grade reading level
3. Context - Explain what it means AND how it's calculated
4. Limitations - Always mention error margins and assumptions
5. Extensibility - Add new algorithms without modifying core
"""

from .base import MetricSchema, ExplainerBase, ExplainedResult
from .registry import ExplainerRegistry
from .ltv_explainer import LTVExplainer
from .mmm_explainer import MMMExplainer
from .eclat_explainer import ECLATExplainer
from .bandit_explainer import ThompsonExplainer, LinUCBExplainer
from .profit_explainer import ProfitExplainer

__all__ = [
    "MetricSchema",
    "ExplainerBase", 
    "ExplainedResult",
    "ExplainerRegistry",
    "LTVExplainer",
    "MMMExplainer",
    "ECLATExplainer",
    "ThompsonExplainer",
    "LinUCBExplainer",
    "ProfitExplainer",
]
