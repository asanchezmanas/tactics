"""
LTV Explainer

Explains metrics from the LTV/Churn prediction engine:
- Customer Lifetime Value (CLV)
- Probability of being alive
- Churn probability
- Expected purchases
- Recency
- Customer segments
"""

from typing import Any, Dict, List, Optional
from .base import (
    ExplainerBase, 
    ExplainedResult, 
    MetricSchema, 
    MetricUnit, 
    MetricDirection
)
from .templates import get_template


class LTVExplainer(ExplainerBase):
    """Explainer for LTV/Churn prediction metrics."""
    
    CATEGORY = "ltv"
    
    def _register_metrics(self) -> None:
        """Register all LTV-related metrics."""
        self._metrics = {
            "clv": MetricSchema(
                id="clv",
                name="Valor de Vida del Cliente",
                name_en="Customer Lifetime Value",
                category=self.CATEGORY,
                unit=MetricUnit.CURRENCY,
                direction=MetricDirection.HIGHER_BETTER,
                typical_range=(50, 2000),
                confidence_available=True,
                decimal_places=0
            ),
            "p_alive": MetricSchema(
                id="p_alive",
                name="Probabilidad Activo",
                name_en="Probability Active",
                category=self.CATEGORY,
                unit=MetricUnit.PERCENTAGE,
                direction=MetricDirection.HIGHER_BETTER,
                typical_range=(0, 1),
                confidence_available=False,
                decimal_places=0
            ),
            "churn_probability": MetricSchema(
                id="churn_probability",
                name="Probabilidad de Churn",
                name_en="Churn Probability",
                category=self.CATEGORY,
                unit=MetricUnit.PERCENTAGE,
                direction=MetricDirection.LOWER_BETTER,
                typical_range=(0, 1),
                confidence_available=False,
                decimal_places=0
            ),
            "expected_purchases": MetricSchema(
                id="expected_purchases",
                name="Compras Esperadas",
                name_en="Expected Purchases",
                category=self.CATEGORY,
                unit=MetricUnit.COUNT,
                direction=MetricDirection.HIGHER_BETTER,
                typical_range=(0, 50),
                confidence_available=True,
                decimal_places=1
            ),
            "recency": MetricSchema(
                id="recency",
                name="Días desde Última Compra",
                name_en="Days Since Last Purchase",
                category=self.CATEGORY,
                unit=MetricUnit.DAYS,
                direction=MetricDirection.LOWER_BETTER,
                typical_range=(0, 365),
                confidence_available=False
            ),
            "segment": MetricSchema(
                id="segment",
                name="Segmento de Cliente",
                name_en="Customer Segment",
                category=self.CATEGORY,
                unit=MetricUnit.SCORE,
                direction=MetricDirection.NEUTRAL,
                typical_range=(0, 4),
                confidence_available=False
            ),
            "revenue_velocity": MetricSchema(
                id="revenue_velocity",
                name="Velocidad de Ingresos",
                name_en="Revenue Velocity",
                category=self.CATEGORY,
                unit=MetricUnit.CURRENCY,
                direction=MetricDirection.HIGHER_BETTER,
                typical_range=(-100, 100),
                confidence_available=False,
                decimal_places=2
            ),
            "attention_weight": MetricSchema(
                id="attention_weight",
                name="Peso de Atención IA",
                name_en="AI Attention Weight",
                category=self.CATEGORY,
                unit=MetricUnit.PERCENTAGE,
                direction=MetricDirection.NEUTRAL,
                typical_range=(0, 1),
                confidence_available=False,
                decimal_places=2
            )
        }
    
    def explain(
        self, 
        metric_id: str, 
        value: Any, 
        context: Optional[Dict] = None
    ) -> ExplainedResult:
        """Generate explanation for an LTV metric."""
        context = context or {}
        schema = self._metrics.get(metric_id)
        
        if not schema:
            return ExplainedResult(
                metric_id=metric_id,
                metric_name=metric_id,
                category=self.CATEGORY,
                value=value,
                formatted_value=str(value),
                what_it_means="Métrica no reconocida.",
                caveats=["Esta métrica no está documentada."]
            )
        
        # Get templates
        template = get_template(self.locale, self.CATEGORY, metric_id)
        
        # Build result
        result = ExplainedResult(
            metric_id=metric_id,
            metric_name=schema.name if self.locale == "es" else schema.name_en,
            category=self.CATEGORY,
            value=value,
            formatted_value=schema.format_value(value, self.locale),
            what_it_means=self.get_what_it_means(metric_id, value),
            how_calculated=self.get_how_calculated(metric_id),
            caveats=self.get_caveats(metric_id, value, context),
            color_hint=self.determine_color(metric_id, value),
            locale=self.locale
        )
        
        # Add confidence interval if available
        if schema.confidence_available and "confidence_interval" in context:
            ci = context["confidence_interval"]
            result.confidence_interval = ci
            result.confidence_level = context.get("confidence_level", 0.95)
            result.formatted_confidence = self.format_confidence_interval(ci, schema)
        
        # Add comparison if available
        if "previous_value" in context:
            prev = context["previous_value"]
            if prev and prev != 0:
                change = ((value - prev) / prev) * 100
                direction = "más" if change > 0 else "menos"
                result.comparison = f"{abs(change):.0f}% {direction} que el período anterior"
        
        # Add sample size if available
        if "sample_size" in context:
            result.sample_size = context["sample_size"]
            if context["sample_size"] < 100:
                result.data_quality = "Baja (pocos datos)"
            elif context["sample_size"] < 500:
                result.data_quality = "Media"
            else:
                result.data_quality = "Alta"
        
        return result
    
    def get_what_it_means(self, metric_id: str, value: Any) -> str:
        """Get plain-language explanation of the metric."""
        template = get_template(self.locale, self.CATEGORY, metric_id)
        return template.get("what_it_means", "")
    
    def get_how_calculated(self, metric_id: str) -> str:
        """Get methodology explanation."""
        template = get_template(self.locale, self.CATEGORY, metric_id)
        return template.get("how_calculated", "")
    
    def get_caveats(
        self, 
        metric_id: str, 
        value: Any, 
        context: Optional[Dict] = None
    ) -> List[str]:
        """Get caveats for this metric."""
        template = get_template(self.locale, self.CATEGORY, metric_id)
        caveats = list(template.get("caveats", []))
        
        context = context or {}
        
        # Add dynamic caveats based on data quality
        if context.get("sample_size", 1000) < 50:
            caveats.insert(0, "⚠️ Pocos datos disponibles. Esta estimación puede ser menos precisa.")
        
        if context.get("data_age_days", 0) > 30:
            caveats.insert(0, "⚠️ Datos con más de 30 días de antigüedad.")
        
        return caveats
