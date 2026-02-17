from fastapi import APIRouter, Depends, HTTPException
from typing import List
from api.auth import CompanyContext, require_tier
from api.database import get_dashboard_metrics, get_high_risk_vips
from core.explainers import ExplainerRegistry

router = APIRouter(prefix="/api/v1")

@router.get("/metrics")
async def api_get_metrics(context: CompanyContext = Depends(require_tier("INTELLIGENCE"))):
    """API endpoint for dashboard metrics."""
    return get_dashboard_metrics(context.company_id)

@router.get("/vips")
async def api_get_vips(context: CompanyContext = Depends(require_tier("OPTIMISATION"))):
    """API endpoint for high-risk VIPs."""
    return get_high_risk_vips(context.company_id)

@router.get("/explain/{category}/{metric_id}")
async def quick_explain(category: str, metric_id: str, value: float, locale: str = "es"):
    """Provides a plain language explanation for a metric."""
    explainer = ExplainerRegistry.get(category)
    if not explainer:
        raise HTTPException(status_code=404, detail=f"Category '{category}' not found")
    
    explainer.locale = locale
    result = explainer.explain(metric_id, value)
    return result.to_dict()
