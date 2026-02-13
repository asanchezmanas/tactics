"""
Integrity Explainer
Translates technical data anomalies into plain language business impact.
Focused on informing and clarifying without stating certainties.
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


class IntegrityExplainer(ExplainerBase):
    """Explainer for Data Integrity and Robustness issues."""
    
    CATEGORY = "integrity"
    
    def _register_metrics(self) -> None:
        """Register all Integrity-related issue types as metrics."""
        self._metrics = {
            "duplicate": MetricSchema(
                id="duplicate",
                name="Duplicidad de Datos",
                name_en="Data Duplication",
                category=self.CATEGORY,
                unit=MetricUnit.COUNT,
                direction=MetricDirection.LOWER_BETTER,
                typical_range=(0, 10),
                confidence_available=False,
                decimal_places=0
            ),
            "gap": MetricSchema(
                id="gap",
                name="Huecos Temporales",
                name_en="Temporal Gaps",
                category=self.CATEGORY,
                unit=MetricUnit.DAYS,
                direction=MetricDirection.LOWER_BETTER,
                typical_range=(0, 7),
                confidence_available=False,
                decimal_places=0
            ),
            "critical_nan": MetricSchema(
                id="critical_nan",
                name="Datos Vitales Faltantes",
                name_en="Missing Vital Data",
                category=self.CATEGORY,
                unit=MetricUnit.COUNT,
                direction=MetricDirection.LOWER_BETTER,
                typical_range=(0, 5),
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
        """Generate human-friendly explanation for an integrity issue."""
        context = context or {}
        schema = self._metrics.get(metric_id)
        
        if not schema:
            return ExplainedResult(
                metric_id=metric_id,
                metric_name=metric_id,
                category=self.CATEGORY,
                value=value,
                formatted_value=str(value),
                what_it_means="Anomalía no reconocida.",
                caveats=["Este tipo de incidencia no está documentado."]
            )
        
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
            icon_hint="security" if metric_id == "duplicate" else "query_builder",
            severity="warning" if value > 0 else "info",
            locale=self.locale
        )
        
        return result
    
    def get_what_it_means(self, metric_id: str, value: Any) -> str:
        """Get plain-language explanation of the anomaly."""
        template = get_template(self.locale, self.CATEGORY, metric_id)
        return template.get("what_it_means", "")
    
    def get_how_calculated(self, metric_id: str) -> str:
        """Get technical detection methodology in plain text."""
        template = get_template(self.locale, self.CATEGORY, metric_id)
        return template.get("how_calculated", "")
    
    def get_caveats(
        self, 
        metric_id: str, 
        value: Any, 
        context: Optional[Dict] = None
    ) -> List[str]:
        """Get caveats and clarifying notes."""
        template = get_template(self.locale, self.CATEGORY, metric_id)
        caveats = list(template.get("caveats", []))
        
        # Add a mandatory clarifying caveat for all integrity explainers
        caveats.append("ℹ️ Esta explicación es una ayuda interpretativa basada en patrones estadísticos, no una certeza absoluta.")
        
        return caveats
