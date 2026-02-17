from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from api.auth import CompanyContext, get_current_user

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/", response_class=HTMLResponse)
@router.get("/{locale}", response_class=HTMLResponse)
async def serve_landing(request: Request, locale: str = "es"):
    """Serves the main landing page."""
    return templates.TemplateResponse("landing/index.html", {"request": request, "locale": locale})

@router.get("/app", response_class=HTMLResponse)
@router.get("/{locale}/app", response_class=HTMLResponse)
async def serve_dashboard(request: Request, locale: str = "es", context: CompanyContext = Depends(get_current_user)):
    return templates.TemplateResponse("app/dashboard.html", {"request": request, "company_id": context.company_id, "locale": locale})

@router.get("/{locale}/app/facturacion", response_class=HTMLResponse)
async def serve_billing(request: Request, locale: str = "es", context: CompanyContext = Depends(get_current_user)):
    return templates.TemplateResponse("app/billing.html", {"request": request, "company_id": context.company_id, "locale": locale})

@router.get("/{locale}/app/configuracion", response_class=HTMLResponse)
async def serve_settings(request: Request, locale: str = "es", context: CompanyContext = Depends(get_current_user)):
    return templates.TemplateResponse("app/settings.html", {"request": request, "company_id": context.company_id, "locale": locale})

@router.get("/{locale}/app/alertas", response_class=HTMLResponse)
async def serve_alerts(request: Request, locale: str = "es", context: CompanyContext = Depends(get_current_user)):
    return templates.TemplateResponse("app/alerts.html", {"request": request, "company_id": context.company_id, "locale": locale})

@router.get("/{locale}/app/asistente", response_class=HTMLResponse)
async def serve_ai_assistant(request: Request, locale: str = "es", context: CompanyContext = Depends(get_current_user)):
    return templates.TemplateResponse("app/ai_assistant.html", {"request": request, "company_id": context.company_id, "locale": locale})

@router.get("/{locale}/app/cohortes", response_class=HTMLResponse)
async def serve_cohorts(request: Request, locale: str = "es", context: CompanyContext = Depends(get_current_user)):
    return templates.TemplateResponse("app/cohorts.html", {"request": request, "company_id": context.company_id, "locale": locale})

@router.get("/{locale}/app/crm", response_class=HTMLResponse)
async def serve_crm(request: Request, locale: str = "es", context: CompanyContext = Depends(get_current_user)):
    return templates.TemplateResponse("app/insights_crm.html", {"request": request, "company_id": context.company_id, "locale": locale})

@router.get("/{locale}/app/analytics", response_class=HTMLResponse)
async def serve_analytics(request: Request, locale: str = "es", context: CompanyContext = Depends(get_current_user)):
    return templates.TemplateResponse("app/mmm_pro.html", {"request": request, "company_id": context.company_id, "locale": locale})

@router.get("/{locale}/app/connectors", response_class=HTMLResponse)
async def serve_connectors(request: Request, locale: str = "es", context: CompanyContext = Depends(get_current_user)):
    return templates.TemplateResponse("app/connectors.html", {"request": request, "company_id": context.company_id, "locale": locale})

@router.get("/{locale}/app/system-health", response_class=HTMLResponse)
async def serve_system_health(request: Request, locale: str = "es", context: CompanyContext = Depends(get_current_user)):
    return templates.TemplateResponse("app/system_health.html", {"request": request, "company_id": context.company_id, "locale": locale})

@router.get("/{locale}/app/calibration-audit", response_class=HTMLResponse)
async def serve_calibration_audit(request: Request, locale: str = "es", context: CompanyContext = Depends(get_current_user)):
    return templates.TemplateResponse("app/calibration_audit.html", {"request": request, "company_id": context.company_id, "locale": locale})

@router.get("/{locale}/app/profile", response_class=HTMLResponse)
async def serve_profile(request: Request, locale: str = "es", context: CompanyContext = Depends(get_current_user)):
    return templates.TemplateResponse("app/profit_matrix.html", {"request": request, "company_id": context.company_id, "locale": locale})
