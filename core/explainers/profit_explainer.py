"""
Profit Explainer

Explains metrics from the Unit Economics engine:
- Net Margin
- Gross Margin
- COGS (Cost of Goods Sold)
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


class ProfitExplainer(ExplainerBase):
    """Explainer for Unit Economics / Profit metrics."""
    
    CATEGORY = "profit"
    
    def _register_metrics(self) -> None:
        """Register all profit-related metrics."""
        self._metrics = {
            "net_margin": MetricSchema(
                id="net_margin",
                name="Margen Neto",
                name_en="Net Margin",
                category=self.CATEGORY,
                unit=MetricUnit.CURRENCY,
                direction=MetricDirection.HIGHER_BETTER,
                typical_range=(-50, 200),
                confidence_available=False,
                decimal_places=2
            ),
            "gross_margin": MetricSchema(
                id="gross_margin",
                name="Margen Bruto",
                name_en="Gross Margin",
                category=self.CATEGORY,
                unit=MetricUnit.CURRENCY,
                direction=MetricDirection.HIGHER_BETTER,
                typical_range=(0, 300),
                confidence_available=False,
                decimal_places=2
            ),
            "cogs": MetricSchema(
                id="cogs",
                name="Coste del Producto",
                name_en="Cost of Goods Sold",
                category=self.CATEGORY,
                unit=MetricUnit.CURRENCY,
                direction=MetricDirection.LOWER_BETTER,
                typical_range=(1, 500),
                confidence_available=False,
                decimal_places=2
            ),
            "gross_margin_pct": MetricSchema(
                id="gross_margin_pct",
                name="Margen Bruto %",
                name_en="Gross Margin %",
                category=self.CATEGORY,
                unit=MetricUnit.PERCENTAGE,
                direction=MetricDirection.HIGHER_BETTER,
                typical_range=(0.2, 0.8),
                confidence_available=False,
                decimal_places=0
            ),
            "net_margin_pct": MetricSchema(
                id="net_margin_pct",
                name="Margen Neto %",
                name_en="Net Margin %",
                category=self.CATEGORY,
                unit=MetricUnit.PERCENTAGE,
                direction=MetricDirection.HIGHER_BETTER,
                typical_range=(0.05, 0.4),
                confidence_available=False,
                decimal_places=0
            )
        }
    
    def explain(
        self, 
        metric_id: str, 
        value: Any, 
        context: Optional[Dict] = None
    ) -> ExplainedResult:
        """Generate explanation for a profit metric."""
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
        
        # Add product name if available
        if "product_name" in context:
            result.what_it_means = f"Para '{context['product_name']}': " + result.what_it_means
        
        # Add profitability warning for negative margins
        if metric_id in ["net_margin", "gross_margin"] and value < 0:
            result.color_hint = "red"
            result.severity = "warning"
        
        return result
    
    def get_what_it_means(self, metric_id: str, value: Any) -> str:
        template = get_template(self.locale, self.CATEGORY, metric_id)
        base = template.get("what_it_means", "")
        
        # Add value-specific interpretation
        if metric_id == "net_margin":
            if value < 0:
                base += f" Con un margen de {value:.2f}€, estás perdiendo dinero en cada venta."
            elif value > 50:
                base += " Este es un margen saludable."
        
        return base
    
    def get_how_calculated(self, metric_id: str) -> str:
        template = get_template(self.locale, self.CATEGORY, metric_id)
        return template.get("how_calculated", "")
    
    def get_caveats(
        self, 
        metric_id: str, 
        value: Any, 
        context: Optional[Dict] = None
    ) -> List[str]:
        template = get_template(self.locale, self.CATEGORY, metric_id)
        caveats = list(template.get("caveats", []))
        
        context = context or {}
        
        if context.get("includes_discounts"):
            caveats.append("Nota: Este cálculo incluye descuentos aplicados.")
        
        if context.get("estimated_cogs"):
            caveats.insert(0, "⚠️ El COGS es una estimación. Actualiza con datos reales para mayor precisión.")
        
        return caveats
