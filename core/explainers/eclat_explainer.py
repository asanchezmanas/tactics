"""
ECLAT Explainer

Explains metrics from the Association Rules engine:
- Support
- Confidence
- Lift
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


class ECLATExplainer(ExplainerBase):
    """Explainer for ECLAT/Association Rules metrics."""
    
    CATEGORY = "eclat"
    
    def _register_metrics(self) -> None:
        """Register all ECLAT-related metrics."""
        self._metrics = {
            "support": MetricSchema(
                id="support",
                name="Frecuencia de Combinación",
                name_en="Support",
                category=self.CATEGORY,
                unit=MetricUnit.PERCENTAGE,
                direction=MetricDirection.HIGHER_BETTER,
                typical_range=(0.01, 0.5),
                confidence_available=False,
                decimal_places=1
            ),
            "confidence": MetricSchema(
                id="confidence",
                name="Confianza de Asociación",
                name_en="Confidence",
                category=self.CATEGORY,
                unit=MetricUnit.PERCENTAGE,
                direction=MetricDirection.HIGHER_BETTER,
                typical_range=(0.1, 0.9),
                confidence_available=False,
                decimal_places=0
            ),
            "lift": MetricSchema(
                id="lift",
                name="Fuerza de Asociación",
                name_en="Lift",
                category=self.CATEGORY,
                unit=MetricUnit.RATIO,
                direction=MetricDirection.HIGHER_BETTER,
                typical_range=(1, 10),
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
        """Generate explanation for an ECLAT metric."""
        context = context or {}
        schema = self._metrics.get(metric_id)
        
        if not schema:
            return ExplainedResult(
                metric_id=metric_id,
                metric_name=metric_id,
                category=self.CATEGORY,
                value=value,
                formatted_value=str(value),
                what_it_means="Métrica no reconocida."
            )
        
        template = get_template(self.locale, self.CATEGORY, metric_id)
        
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
        
        # Add product names if available
        if "product_a" in context and "product_b" in context:
            result.what_it_means = result.what_it_means.replace(
                "producto A", context["product_a"]
            ).replace(
                "producto B", context["product_b"]
            )
        
        # Add sample size
        if "total_orders" in context:
            result.sample_size = context["total_orders"]
        
        return result
    
    def get_what_it_means(self, metric_id: str, value: Any) -> str:
        """Get plain-language explanation."""
        template = get_template(self.locale, self.CATEGORY, metric_id)
        base = template.get("what_it_means", "")
        
        # Add interpretation
        if metric_id == "lift":
            if value < 1:
                base += " Un lift menor a 1 significa que estos productos se compran juntos MENOS de lo esperado."
            elif value > 3:
                base += " Este es un lift muy fuerte, indicando una asociación significativa."
        
        return base
    
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
        
        # Low support warning
        if metric_id == "support" and value < 0.05:
            caveats.insert(0, "⚠️ Soporte bajo (<5%). Esta combinación es poco frecuente.")
        
        # Low lift warning
        if metric_id == "lift" and 0.9 <= value <= 1.1:
            caveats.insert(0, "Lift cercano a 1: no hay relación especial entre estos productos.")
        
        return caveats
