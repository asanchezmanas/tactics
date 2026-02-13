"""
MMM Explainer

Explains metrics from the Media Mix Modeling engine:
- ROAS (Return on Ad Spend)
- Saturation
- Contribution
- Optimal Budget
- Adstock
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


class MMMExplainer(ExplainerBase):
    """Explainer for Media Mix Modeling metrics."""
    
    CATEGORY = "mmm"
    
    def _register_metrics(self) -> None:
        """Register all MMM-related metrics."""
        self._metrics = {
            "roas": MetricSchema(
                id="roas",
                name="Retorno sobre Inversión Publicitaria",
                name_en="Return on Ad Spend",
                category=self.CATEGORY,
                unit=MetricUnit.RATIO,
                direction=MetricDirection.HIGHER_BETTER,
                typical_range=(0.5, 10),
                confidence_available=True,
                decimal_places=2
            ),
            "saturation": MetricSchema(
                id="saturation",
                name="Nivel de Saturación",
                name_en="Saturation Level",
                category=self.CATEGORY,
                unit=MetricUnit.PERCENTAGE,
                direction=MetricDirection.LOWER_BETTER,
                typical_range=(0, 1),
                confidence_available=False,
                decimal_places=0
            ),
            "contribution": MetricSchema(
                id="contribution",
                name="Contribución del Canal",
                name_en="Channel Contribution",
                category=self.CATEGORY,
                unit=MetricUnit.CURRENCY,
                direction=MetricDirection.HIGHER_BETTER,
                typical_range=(0, 100000),
                confidence_available=True,
                decimal_places=0
            ),
            "optimal_budget": MetricSchema(
                id="optimal_budget",
                name="Presupuesto Óptimo",
                name_en="Optimal Budget",
                category=self.CATEGORY,
                unit=MetricUnit.CURRENCY,
                direction=MetricDirection.NEUTRAL,
                typical_range=(0, 50000),
                confidence_available=True,
                decimal_places=0
            ),
            "adstock": MetricSchema(
                id="adstock",
                name="Efecto Residual",
                name_en="Adstock Effect",
                category=self.CATEGORY,
                unit=MetricUnit.DAYS,
                direction=MetricDirection.NEUTRAL,
                typical_range=(1, 30),
                confidence_available=False,
                decimal_places=0
            ),
            "synergy_index": MetricSchema(
                id="synergy_index",
                name="Índice de Sinergia",
                name_en="Synergy Index",
                category=self.CATEGORY,
                unit=MetricUnit.RATIO,
                direction=MetricDirection.HIGHER_BETTER,
                typical_range=(1, 5),
                confidence_available=False,
                decimal_places=2
            ),
            "multi_objective_balance": MetricSchema(
                id="multi_objective_balance",
                name="Equilibrio de Objetivos",
                name_en="Multi-Objective balance",
                category=self.CATEGORY,
                unit=MetricUnit.PERCENTAGE,
                direction=MetricDirection.NEUTRAL,
                typical_range=(0, 1),
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
        """Generate explanation for an MMM metric."""
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
        
        # Add channel-specific context
        if "channel" in context:
            result.what_it_means = result.what_it_means.replace(
                "este canal", 
                context["channel"]
            )
        
        # Confidence interval
        if schema.confidence_available and "confidence_interval" in context:
            ci = context["confidence_interval"]
            result.confidence_interval = ci
            result.confidence_level = context.get("confidence_level", 0.95)
            result.formatted_confidence = self.format_confidence_interval(ci, schema)
        
        # Benchmark comparison
        if "industry_average" in context:
            avg = context["industry_average"]
            if value > avg:
                diff = ((value - avg) / avg) * 100
                result.benchmark = f"Por encima del promedio del sector ({diff:.0f}% mejor)"
            else:
                diff = ((avg - value) / avg) * 100
                result.benchmark = f"Por debajo del promedio del sector ({diff:.0f}% menos)"
        
        return result
    
    def get_what_it_means(self, metric_id: str, value: Any) -> str:
        """Get plain-language explanation."""
        template = get_template(self.locale, self.CATEGORY, metric_id)
        base = template.get("what_it_means", "")
        
        # Add value-specific context for ROAS
        if metric_id == "roas":
            if value < 1:
                base += f" Con un ROAS de {value:.1f}x, estás perdiendo dinero en este canal."
            elif value >= 5:
                base += f" Un ROAS de {value:.1f}x es excelente."
            elif value >= 3:
                base += f" Un ROAS de {value:.1f}x es saludable."
        
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
        
        # Add dynamic caveats
        if context.get("data_months", 12) < 3:
            caveats.insert(0, "⚠️ Menos de 3 meses de datos. Los resultados pueden ser menos confiables.")
        
        if context.get("seasonality_detected"):
            caveats.append("Nota: Se ha detectado estacionalidad en los datos.")
        
        return caveats
