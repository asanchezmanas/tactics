"""
Base Classes for Explainer Engine

Provides the foundational abstractions:
- MetricSchema: Definition of metrics with metadata
- ExplainerBase: Abstract interface for all explainers
- ExplainedResult: Standardized output format
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime
from enum import Enum


class MetricUnit(Enum):
    """Units for metric values."""
    CURRENCY = "currency"
    PERCENTAGE = "percentage"
    RATIO = "ratio"
    COUNT = "count"
    DAYS = "days"
    SCORE = "score"


class MetricDirection(Enum):
    """Whether higher or lower values are better."""
    HIGHER_BETTER = "higher_better"
    LOWER_BETTER = "lower_better"
    NEUTRAL = "neutral"


@dataclass
class MetricSchema:
    """
    Defines the structure and metadata of a metric for explanation purposes.
    
    This schema provides all the context needed to generate meaningful
    explanations without hard-coding knowledge into explainers.
    """
    id: str                           # Unique identifier: "clv", "roas", etc.
    name: str                         # Human-readable: "Valor de Vida del Cliente"
    name_en: str                      # English name
    category: str                     # Algorithm category: "ltv", "mmm", "eclat"
    unit: MetricUnit                  # How to format the value
    direction: MetricDirection        # Higher/lower = better?
    typical_range: Tuple[float, float]  # Expected value range
    confidence_available: bool = False  # Does this metric have confidence intervals?
    
    # Formatting helpers
    decimal_places: int = 2
    currency_symbol: str = "€"
    
    def format_value(self, value: float, locale: str = "es") -> str:
        """Format the raw value for display."""
        if self.unit == MetricUnit.CURRENCY:
            return f"{self.currency_symbol}{value:,.{self.decimal_places}f}"
        elif self.unit == MetricUnit.PERCENTAGE:
            return f"{value * 100:.{self.decimal_places}f}%"
        elif self.unit == MetricUnit.RATIO:
            return f"{value:.{self.decimal_places}f}x"
        elif self.unit == MetricUnit.DAYS:
            return f"{int(value)} días" if locale == "es" else f"{int(value)} days"
        elif self.unit == MetricUnit.COUNT:
            return f"{int(value):,}"
        else:
            return f"{value:.{self.decimal_places}f}"


@dataclass
class ExplainedResult:
    """
    Standardized output for all metric explanations.
    
    This is the contract between explainers and the UI. Every explanation
    follows this structure to ensure consistency across all algorithms.
    """
    # Identification
    metric_id: str
    metric_name: str
    category: str
    
    # Primary value
    value: Any
    formatted_value: str
    
    # Uncertainty (when available)
    confidence_interval: Optional[Tuple[float, float]] = None
    confidence_level: Optional[float] = None  # e.g., 0.95 for 95%
    formatted_confidence: Optional[str] = None
    
    # Plain language explanations
    what_it_means: str = ""
    how_calculated: str = ""
    caveats: List[str] = field(default_factory=list)
    
    # Contextual comparisons
    comparison: Optional[str] = None      # "23% más que el mes anterior"
    benchmark: Optional[str] = None       # "Por encima del promedio"
    trend: Optional[str] = None           # "Subiendo", "Bajando", "Estable"
    
    # Data quality indicators
    data_freshness: Optional[str] = None  # "Actualizado hace 2 horas"
    sample_size: Optional[int] = None     # How many data points
    data_quality: Optional[str] = None    # "Alta", "Media", "Baja"
    
    # UI hints
    color_hint: str = "neutral"           # "green", "yellow", "red", "neutral"
    icon_hint: str = "info"               # For frontend icon selection
    severity: str = "info"                # "info", "success", "warning", "error"
    
    # Metadata
    generated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    explainer_version: str = "1.0.0"
    locale: str = "es"
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "metric_id": self.metric_id,
            "metric_name": self.metric_name,
            "category": self.category,
            "value": self.value,
            "formatted_value": self.formatted_value,
            "confidence_interval": self.confidence_interval,
            "confidence_level": self.confidence_level,
            "formatted_confidence": self.formatted_confidence,
            "what_it_means": self.what_it_means,
            "how_calculated": self.how_calculated,
            "caveats": self.caveats,
            "comparison": self.comparison,
            "benchmark": self.benchmark,
            "trend": self.trend,
            "data_freshness": self.data_freshness,
            "sample_size": self.sample_size,
            "data_quality": self.data_quality,
            "color_hint": self.color_hint,
            "icon_hint": self.icon_hint,
            "severity": self.severity,
            "generated_at": self.generated_at,
            "locale": self.locale
        }


class ExplainerBase(ABC):
    """
    Abstract base class for all algorithm explainers.
    
    Each algorithm (LTV, MMM, ECLAT, etc.) should have its own explainer
    that inherits from this class and implements the required methods.
    
    This ensures consistency and makes adding new algorithms trivial.
    """
    
    def __init__(self, locale: str = "es"):
        self.locale = locale
        self._metrics: Dict[str, MetricSchema] = {}
        self._register_metrics()
    
    @abstractmethod
    def _register_metrics(self) -> None:
        """
        Register all metrics this explainer handles.
        Called during initialization.
        """
        pass
    
    def get_supported_metrics(self) -> List[str]:
        """Return list of metric IDs this explainer handles."""
        return list(self._metrics.keys())
    
    def get_metric_schema(self, metric_id: str) -> Optional[MetricSchema]:
        """Get the schema for a specific metric."""
        return self._metrics.get(metric_id)
    
    @abstractmethod
    def explain(
        self, 
        metric_id: str, 
        value: Any, 
        context: Optional[Dict] = None
    ) -> ExplainedResult:
        """
        Generate human-readable explanation for a metric value.
        
        Args:
            metric_id: The metric to explain (e.g., "clv", "roas")
            value: The raw metric value
            context: Optional additional context (e.g., historical data,
                     confidence intervals, sample sizes)
        
        Returns:
            ExplainedResult with all explanation components
        """
        pass
    
    @abstractmethod
    def get_what_it_means(self, metric_id: str, value: Any) -> str:
        """Return plain-language explanation of what this metric represents."""
        pass
    
    @abstractmethod
    def get_how_calculated(self, metric_id: str) -> str:
        """Return plain-language explanation of the calculation methodology."""
        pass
    
    @abstractmethod
    def get_caveats(self, metric_id: str, value: Any, context: Optional[Dict] = None) -> List[str]:
        """Return list of limitations, assumptions, and caveats."""
        pass
    
    def determine_color(self, metric_id: str, value: float) -> str:
        """
        Determine color hint based on value and metric direction.
        
        Returns: "green", "yellow", "red", or "neutral"
        """
        schema = self._metrics.get(metric_id)
        if not schema:
            return "neutral"
        
        low, high = schema.typical_range
        mid = (low + high) / 2
        
        if schema.direction == MetricDirection.HIGHER_BETTER:
            if value >= high * 0.8:
                return "green"
            elif value >= mid:
                return "yellow"
            else:
                return "red"
        elif schema.direction == MetricDirection.LOWER_BETTER:
            if value <= low * 1.2:
                return "green"
            elif value <= mid:
                return "yellow"
            else:
                return "red"
        
        return "neutral"
    
    def format_confidence_interval(
        self, 
        ci: Tuple[float, float], 
        schema: MetricSchema
    ) -> str:
        """Format confidence interval for display."""
        low_fmt = schema.format_value(ci[0], self.locale)
        high_fmt = schema.format_value(ci[1], self.locale)
        return f"{low_fmt} - {high_fmt}"
