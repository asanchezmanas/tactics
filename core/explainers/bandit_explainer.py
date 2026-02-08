"""
Bandit Explainers

Explains metrics from the Multi-Armed Bandit engines:
- Thompson Sampling: conversion rate, samples, prob_best
- LinUCB: ucb_score, exploitation, exploration
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


class ThompsonExplainer(ExplainerBase):
    """Explainer for Thompson Sampling A/B test metrics."""
    
    CATEGORY = "thompson"
    
    def _register_metrics(self) -> None:
        """Register Thompson Sampling metrics."""
        self._metrics = {
            "conversion_rate": MetricSchema(
                id="conversion_rate",
                name="Tasa de Conversión",
                name_en="Conversion Rate",
                category=self.CATEGORY,
                unit=MetricUnit.PERCENTAGE,
                direction=MetricDirection.HIGHER_BETTER,
                typical_range=(0.01, 0.20),
                confidence_available=True,
                decimal_places=1
            ),
            "samples": MetricSchema(
                id="samples",
                name="Muestras",
                name_en="Samples",
                category=self.CATEGORY,
                unit=MetricUnit.COUNT,
                direction=MetricDirection.HIGHER_BETTER,
                typical_range=(10, 10000),
                confidence_available=False
            ),
            "prob_best": MetricSchema(
                id="prob_best",
                name="Probabilidad de Ser la Mejor",
                name_en="Probability of Being Best",
                category=self.CATEGORY,
                unit=MetricUnit.PERCENTAGE,
                direction=MetricDirection.HIGHER_BETTER,
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
        """Generate explanation for a Thompson Sampling metric."""
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
        
        # Add variant name if available
        if "variant_name" in context:
            result.what_it_means = f"Variante '{context['variant_name']}': " + result.what_it_means
        
        if "sample_size" in context:
            result.sample_size = context["sample_size"]
        
        return result
    
    def get_what_it_means(self, metric_id: str, value: Any) -> str:
        template = get_template(self.locale, self.CATEGORY, metric_id)
        return template.get("what_it_means", "")
    
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
        
        if context.get("sample_size", 1000) < 100:
            caveats.insert(0, "⚠️ Menos de 100 muestras. Los resultados son preliminares.")
        
        return caveats


class LinUCBExplainer(ExplainerBase):
    """Explainer for LinUCB contextual bandit metrics."""
    
    CATEGORY = "linucb"
    
    def _register_metrics(self) -> None:
        """Register LinUCB metrics."""
        self._metrics = {
            "ucb_score": MetricSchema(
                id="ucb_score",
                name="Puntuación UCB",
                name_en="UCB Score",
                category=self.CATEGORY,
                unit=MetricUnit.SCORE,
                direction=MetricDirection.HIGHER_BETTER,
                typical_range=(0, 10),
                confidence_available=False,
                decimal_places=2
            ),
            "exploitation": MetricSchema(
                id="exploitation",
                name="Valor Estimado",
                name_en="Estimated Value",
                category=self.CATEGORY,
                unit=MetricUnit.SCORE,
                direction=MetricDirection.HIGHER_BETTER,
                typical_range=(0, 5),
                confidence_available=False,
                decimal_places=2
            ),
            "exploration": MetricSchema(
                id="exploration",
                name="Bonus de Incertidumbre",
                name_en="Uncertainty Bonus",
                category=self.CATEGORY,
                unit=MetricUnit.SCORE,
                direction=MetricDirection.NEUTRAL,
                typical_range=(0, 5),
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
        """Generate explanation for a LinUCB metric."""
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
            color_hint="neutral",  # LinUCB scores are relative
            locale=self.locale
        )
        
        return result
    
    def get_what_it_means(self, metric_id: str, value: Any) -> str:
        template = get_template(self.locale, self.CATEGORY, metric_id)
        return template.get("what_it_means", "")
    
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
        return caveats
