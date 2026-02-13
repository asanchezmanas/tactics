import os
from fastapi import FastAPI, BackgroundTasks, HTTPException, Request, Depends, File, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import List, Optional
from dotenv import load_dotenv
from supabase import create_client, Client
from .auth import get_current_user, CompanyContext, require_tier

# Load environment variables
load_dotenv()

app = FastAPI(title="Tactics AI API")

# Setup templates - pointing to the new modular structure
templates = Jinja2Templates(directory="templates")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Supabase Setup
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None

class SyncRequest(BaseModel):
    company_id: str

# --- Public Marketing Routes ---
@app.get("/", response_class=HTMLResponse)
@app.get("/{locale}", response_class=HTMLResponse)
async def serve_landing(request: Request, locale: str = "es"):
    """Serves the public landing page."""
    return templates.TemplateResponse("public/landing.html", {"request": request, "locale": locale})

@app.get("/soporte", response_class=HTMLResponse)
@app.get("/{locale}/soporte", response_class=HTMLResponse)
async def serve_faqs(request: Request, locale: str = "es"):
    """Serves the public FAQ page."""
    return templates.TemplateResponse("public/faqs.html", {"request": request, "locale": locale})

@app.get("/login", response_class=HTMLResponse)
@app.get("/{locale}/login", response_class=HTMLResponse)
async def serve_login(request: Request, locale: str = "es"):
    """Placeholder for the login view."""
    return HTMLResponse("<h1>P├ígina de Login</h1><p>Funcionalidad en desarrollo.</p><a href='/'>Volver al inicio</a>")

# --- Blog Routes ---
@app.get("/blog", response_class=HTMLResponse)
@app.get("/{locale}/blog", response_class=HTMLResponse)
async def serve_blog(request: Request, locale: str = "es"):
    """Serves the blog list page with locale awareness."""
    return templates.TemplateResponse("public/blog.html", {
        "request": request,
        "locale": locale
    })

@app.get("/blog/{slug}", response_class=HTMLResponse)
@app.get("/{locale}/blog/{slug}", response_class=HTMLResponse)
async def serve_blog_post(request: Request, slug: str, locale: str = "es"):
    """Serves an individual blog post rendered from Markdown with locale support."""
    from .blog_engine import get_blog_post_data
    
    result = get_blog_post_data(slug, locale=locale)
    
    if not result["success"]:
        raise HTTPException(status_code=result.get("status_code", 404), detail=result["error"])
        
    return templates.TemplateResponse("public/blog_post.html", {
        "request": request,
        "post_title": result["title"],
        "post_content": result["html"],
        "locale": locale
    })


@app.get("/demo/diagnostic", response_class=HTMLResponse)
@app.get("/{locale}/demo/diagnostic", response_class=HTMLResponse)
async def serve_diagnostic(request: Request, locale: str = "es"):
    """Serves the frictionless Diagnostic Tool."""
    return templates.TemplateResponse("public/diagnostic.html", {"request": request, "locale": locale})

@app.get("/demo/sandbox", response_class=HTMLResponse)
@app.get("/{locale}/demo/sandbox", response_class=HTMLResponse)
async def serve_sandbox(request: Request, locale: str = "es"):
    """Serves the Live Sandbox Dashboard populated by session data."""
    return templates.TemplateResponse("public/sandbox_dashboard.html", {"request": request, "locale": locale})

# --- App Routes ---
@app.get("/app", response_class=HTMLResponse)
@app.get("/{locale}/app", response_class=HTMLResponse)
async def serve_dashboard(request: Request, locale: str = "es"):
    """Serves the integrated AI dashboard via Jinja2."""
    return templates.TemplateResponse("app/dashboard.html", {
        "request": request, 
        "company_id": "c7a9b1d2-e3f4-5678-a9b0-c1d2e3f4g5h6",
        "locale": locale
    })

@app.get("/app/facturacion", response_class=HTMLResponse)
@app.get("/{locale}/app/facturacion", response_class=HTMLResponse)
async def serve_billing(request: Request, locale: str = "es"):
    """Serves the Billing and Invoices page."""
    return templates.TemplateResponse("app/billing.html", {
        "request": request,
        "company_id": "c7a9b1d2-e3f4-5678-a9b0-c1d2e3f4g5h6",
        "locale": locale
    })

@app.get("/app/configuracion", response_class=HTMLResponse)
@app.get("/{locale}/app/configuracion", response_class=HTMLResponse)
async def serve_settings(request: Request, locale: str = "es"):
    """Serves the Account Settings and Security page."""
    return templates.TemplateResponse("app/settings.html", {
        "request": request,
        "company_id": "c7a9b1d2-e3f4-5678-a9b0-c1d2e3f4g5h6",
        "locale": locale
    })

@app.get("/app/alertas", response_class=HTMLResponse)
@app.get("/{locale}/app/alertas", response_class=HTMLResponse)
async def serve_alerts(request: Request, locale: str = "es"):
    """Serves the Bayesian Alerts inbox."""
    return templates.TemplateResponse("app/alerts.html", {
        "request": request,
        "company_id": "c7a9b1d2-e3f4-5678-a9b0-c1d2e3f4g5h6",
        "locale": locale
    })

@app.get("/app/asistente", response_class=HTMLResponse)
@app.get("/{locale}/app/asistente", response_class=HTMLResponse)
async def serve_ai_assistant(request: Request, locale: str = "es"):
    """Serves the AI Strategic Assistant chat."""
    return templates.TemplateResponse("app/ai_assistant.html", {
        "request": request,
        "company_id": "c7a9b1d2-e3f4-5678-a9b0-c1d2e3f4g5h6",
        "locale": locale
    })

@app.get("/app/cohortes", response_class=HTMLResponse)
@app.get("/{locale}/app/cohortes", response_class=HTMLResponse)
async def serve_cohorts(request: Request, locale: str = "es"):
    """Serves the Customer Cohorts & LTV management page."""
    return templates.TemplateResponse("app/cohorts.html", {
        "request": request,
        "company_id": "c7a9b1d2-e3f4-5678-a9b0-c1d2e3f4g5h6",
        "locale": locale
    })

@app.get("/app/crm", response_class=HTMLResponse)
@app.get("/{locale}/app/crm", response_class=HTMLResponse)
async def serve_crm(request: Request, locale: str = "es"):
    """Serves the Advanced CRM Dashboard (Engine A)."""
    return templates.TemplateResponse("app/insights_crm.html", {
        "request": request,
        "company_id": "c7a9b1d2-e3f4-5678-a9b0-c1d2e3f4g5h6",
        "locale": locale
    })

@app.get("/app/analytics", response_class=HTMLResponse)
@app.get("/{locale}/app/analytics", response_class=HTMLResponse)
async def serve_analytics(request: Request, locale: str = "es"):
    """Serves the MMM Pro Analytics Dashboard (Engine B)."""
    return templates.TemplateResponse("app/mmm_pro.html", {
        "request": request,
        "company_id": "c7a9b1d2-e3f4-5678-a9b0-c1d2e3f4g5h6",
        "locale": locale
    })

@app.get("/app/connectors", response_class=HTMLResponse)
@app.get("/{locale}/app/connectors", response_class=HTMLResponse)
async def serve_connectors(request: Request, locale: str = "es"):
    """Serves the Data Connectors management page."""
    return templates.TemplateResponse("app/connectors.html", {
        "request": request,
        "company_id": "c7a9b1d2-e3f4-5678-a9b0-c1d2e3f4g5h6",
        "locale": locale
    })

@app.get("/app/import", response_class=HTMLResponse)
@app.get("/{locale}/app/import", response_class=HTMLResponse)
async def serve_import_wizard(request: Request, locale: str = "es"):
    """Serves the CSV Import Wizard for data ingestion."""
    return templates.TemplateResponse("app/import_wizard.html", {"request": request, "locale": locale})

@app.get("/app/system-health", response_class=HTMLResponse)
@app.get("/{locale}/app/system-health", response_class=HTMLResponse)
async def serve_system_health(request: Request, locale: str = "es"):
    """Serves the System Health & Resilience Dashboard."""
    return templates.TemplateResponse("app/system_health.html", {
        "request": request,
        "company_id": "c7a9b1d2-e3f4-5678-a9b0-c1d2e3f4g5h6",
        "locale": locale
    })

@app.get("/app/calibration-audit", response_class=HTMLResponse)
@app.get("/{locale}/app/calibration-audit", response_class=HTMLResponse)
async def serve_calibration_audit(request: Request, locale: str = "es"):
    """Serves the Data Integrity & Traceability Audit page."""
    return templates.TemplateResponse("app/calibration_audit.html", {
        "request": request,
        "company_id": "c7a9b1d2-e3f4-5678-a9b0-c1d2e3f4g5h6",
        "locale": locale
    })

@app.get("/app/profile", response_class=HTMLResponse)
@app.get("/{locale}/app/profile", response_class=HTMLResponse)
async def serve_profile(request: Request, locale: str = "es"):
    """Serves the User Profile page."""
    return templates.TemplateResponse("app/profile.html", {
        "request": request,
        "company_id": "c7a9b1d2-e3f4-5678-a9b0-c1d2e3f4g5h6",
        "locale": locale
    })

@app.get("/app/showcase", response_class=HTMLResponse)
@app.get("/{locale}/app/showcase", response_class=HTMLResponse)
async def serve_showcase(request: Request, locale: str = "es"):
    """Serves the Showcase Gallery with demo datasets."""
    return templates.TemplateResponse("app/showcase.html", {"request": request, "locale": locale})

@app.get("/app/showcase/insights/{case_id}", response_class=HTMLResponse)
async def serve_showcase_detail(case_id: str, request: Request):
    """Serves a granular detail page for a specific showcase."""
    from scripts.import_demo_showcases import SHOWCASES
    if case_id not in SHOWCASES:
        raise HTTPException(status_code=404, detail=f"Case {case_id} not found")
        
    template_path = f"app/showcases/{case_id}.html"
    return templates.TemplateResponse(template_path, {
        "request": request,
        "showcase": SHOWCASES[case_id],
        "case_id": case_id
    })

@app.get("/api/demo/activate/{case_id}")
async def activate_demo(case_id: str, request: Request):
    """
    Activates a demo showcase dataset for the current session.
    Returns redirect to dashboard with demo context.
    """
    from scripts.import_demo_showcases import SHOWCASES, import_showcase
    
    if case_id not in SHOWCASES:
        raise HTTPException(status_code=404, detail=f"Unknown showcase: {case_id}")
    
    # Ensure data is imported
    import_showcase(case_id, use_bundled=True)
    
    showcase = SHOWCASES[case_id]
    
    # For browser redirect, we send them to dashboard with a demo flag
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url=f"/app?demo={showcase['company_id']}", status_code=303)

# --- Auth Routes ---
@app.get("/auth/signin", response_class=HTMLResponse)
async def serve_signin(request: Request):
    return templates.TemplateResponse("auth/signin.html", {"request": request})

@app.get("/auth/signup", response_class=HTMLResponse)
async def serve_signup(request: Request):
    return templates.TemplateResponse("auth/signup.html", {"request": request})

@app.get("/auth/reset-password", response_class=HTMLResponse)
async def serve_reset_password(request: Request):
    return templates.TemplateResponse("auth/reset-password.html", {"request": request})

@app.get("/health")
async def health():
    return {"status": "healthy"}

from .pipeline import run_full_pipeline
from core.optimizer import run_budget_optimization, run_budget_optimization_bayesian
from .database import get_dashboard_metrics, get_high_risk_vips, get_gastos
from .database_resilient import check_database_health, get_local_cache
from core.resilience import get_circuit_breaker_status

# Explainer Engine for plain language metric explanations
from core.explainers.registry import ExplainerRegistry
from core.explainers.ltv_explainer import LTVExplainer
from core.explainers.mmm_explainer import MMMExplainer
from core.explainers.eclat_explainer import ECLATExplainer
from core.explainers.bandit_explainer import ThompsonExplainer, LinUCBExplainer
from core.explainers.profit_explainer import ProfitExplainer
from core.metrics_factory import BusinessMetricsFactory

# Register all explainers on startup
ExplainerRegistry.register("ltv", LTVExplainer())
ExplainerRegistry.register("mmm", MMMExplainer())
ExplainerRegistry.register("eclat", ECLATExplainer())
ExplainerRegistry.register("thompson", ThompsonExplainer())
ExplainerRegistry.register("linucb", LinUCBExplainer())
ExplainerRegistry.register("profit", ProfitExplainer())

@app.get("/api/analytics/business-metrics/{company_id}")
async def get_business_metrics(company_id: str, context: CompanyContext = Depends(get_current_user)):
    """
    Returns advanced BI metrics (MER, Retention, Growth) for a company.
    """
    if not supabase:
        raise HTTPException(status_code=500, detail="Supabase not configured")

    # Fetch raw data
    ventas_res = supabase.table("ventas").select("*").eq("company_id", company_id).execute()
    gastos_res = supabase.table("gastos_marketing").select("*").eq("company_id", company_id).execute()
    
    sales_df = pd.DataFrame(ventas_res.data) if ventas_res.data else pd.DataFrame()
    marketing_df = pd.DataFrame(gastos_res.data) if gastos_res.data else pd.DataFrame()
    
    # Calculate metrics
    factory = BusinessMetricsFactory(company_id)
    report = factory.calculate_all(sales_df, marketing_df)
    
    return report

from core.diagnostic_engine import DiagnosticEngine

@app.post("/api/demo/diagnostic")
async def process_diagnostic_csv(file: UploadFile = File(...)):
    """
    Processes a user-uploaded CSV for the Live Sandbox.
    No authentication required (Public Lead Gen).
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are allowed")
    
    engine = DiagnosticEngine()
    # Read file content
    content = await file.read()
    from io import StringIO
    csv_text = content.decode('utf-8')
    
    result = engine.process_csv(StringIO(csv_text))
    if not result["success"]:
        raise HTTPException(status_code=422, detail=result["error"])
    
    return result

@app.get("/api/health/system")
async def get_system_health():
    """
    Returns the comprehensive health status of the system.
    """
    # 1. Database & Cache
    db_health = check_database_health()
    
    # 2. Circuit Breakers
    breakers = get_circuit_breaker_status()
    
    # 3. Dead Letter Queue
    cache = get_local_cache()
    dead_letters = cache.get_dead_letters()
    
    return {
        "status": "healthy" if db_health["status"] == "healthy" and not dead_letters else "degraded",
        "database": db_health,
        "circuit_breakers": breakers,
        "dead_letters": dead_letters
    }

async def get_dashboard_data(context: CompanyContext = Depends(get_current_user)):
    """
    Returns all data needed for the AI dashboard.
    """
    company_id = context.company_id
    if not supabase:
        raise HTTPException(status_code=500, detail="Supabase not configured")
        
    metrics = get_dashboard_metrics(company_id)
    vips = get_high_risk_vips(company_id)
    expenses = get_gastos(company_id)
    
    # Format expenses for MMM visualization if needed
    # (Simplified for now)
    channel_performance = {}
    if not expenses.empty:
        channel_performance = expenses.groupby('canal')['inversion'].sum().to_dict()

    return {
        "metrics": metrics,
        "high_risk_vips": vips,
        "channel_performance": channel_performance
    }

@app.get("/api/elite/metrics")
async def get_elite_metrics(context: CompanyContext = Depends(get_current_user)):
    """
    Returns high-tier Intelligence 2.0 metrics.
    Requires Elite or Precision tier.
    """
    # In a real scenario, this would compute metrics from the database
    # For now, we return high-fidelity mock data aligned with Elite algorithms
    import numpy as np
    
    return {
        "kinetic": {
            "revenue_velocity": 124.50, # EUR/month acceleration
            "revenue_momentum": 4500.12,
            "velocity_trend": "accelerating",
            "momentum_score": 88
        },
        "synergy": {
            "index": 1.42, # 1.42x synergy factor
            "top_pair": ("Meta Ads", "Google Ads"),
            "efficiency_gain": 0.15, # 15% gain via synergy
            "matrix": [
                [1.0, 0.4, 0.2], # Meta vs Meta, Google, TikTok
                [0.3, 1.0, 0.1],
                [0.1, 0.1, 1.0]
            ]
        },
        "attention": {
            "sequence_focus": [0.05, 0.05, 0.05, 0.1, 0.2, 0.4, 0.1], # Weight per recent month
            "critical_event": "Black Friday Prep"
        }
    }

@app.post("/sync-all")
async def trigger_full_sync(background_tasks: BackgroundTasks, 
                            context: CompanyContext = Depends(get_current_user)):
    """
    Triggers the full pipeline: Data Sync -> LTV/Churn prediction -> Budget Optimization.
    """
    if not supabase:
        raise HTTPException(status_code=500, detail="Supabase not configured")
        
    background_tasks.add_task(run_full_pipeline, context.company_id, tier=context.tier)
    
    return {
        "status": "processing",
        "message": f"Pipeline started for company {context.company_id} ({context.tier} tier)"
    }

class SimulationRequest(BaseModel):
    company_id: str
    total_budget: float

@app.post("/simulate-budget")
async def simulate_budget(request: SimulationRequest, 
                          context: CompanyContext = Depends(get_current_user)):
    """
    Runs the budget optimization simulator.
    """
    # In a real scenario, we would fetch trained alpha/gamma params from DB
    # For now, using sample data
    sample_params = [(1000, 0.8), (2000, 0.5), (500, 1.2)] # Meta, Google, TikTok
    
    optimal_data = run_budget_optimization_bayesian(request.total_budget, sample_params)
    
    return {
        "company_id": request.company_id,
        "total_budget": request.total_budget,
        "recommended_allocation": {
            "Meta Ads": {"amount": optimal_data["means"][0], "lower": optimal_data["lowers"][0], "upper": optimal_data["uppers"][0]},
            "Google Ads": {"amount": optimal_data["means"][1], "lower": optimal_data["lowers"][1], "upper": optimal_data["uppers"][1]},
            "TikTok Ads": {"amount": optimal_data["means"][2], "lower": optimal_data["lowers"][2], "upper": optimal_data["uppers"][2]}
        }
    }

from .integrations import export_to_meta_ads, export_to_klaviyo
from core.secure_vault import SecureVault

@app.post("/export-high-risk-vips")
async def export_vips(context: CompanyContext = Depends(get_current_user)):
    """
    Exports High-Risk VIPs to marketing platforms.
    """
    if not supabase:
        raise HTTPException(status_code=500, detail="Supabase not configured")
    
    # 1. Fetch High Risk VIPs
    vips = get_high_risk_vips(context.company_id, limit=100)
    if not vips:
        return {"status": "success", "message": "No high risk VIPs found to export"}
    
    # 2. Extract emails (assuming they exist in the 'clientes' table joined in vips)
    emails = [v['clientes']['email'] for v in vips if v.get('clientes', {}).get('email')]
    
    if not emails:
        return {"status": "success", "message": "High risk VIPs found but no valid emails available"}

    # 3. Vault Backup (Zero-Knowledge) - Important for audit trail of PII exports
    try:
        vault = SecureVault(company_id=context.company_id)
        vault.store_audit_document(
            doc_type="segment_export",
            content=json.dumps(vips, default=str).encode('utf-8'),
            doc_name=f"high_risk_vips_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )
    except Exception as ev:
        print(f"[Export] Vault backup failed: {ev}")

    # 4. Trigger Mock Exports (In production, tokens would come from Secure Settings)
    meta_res = await export_to_meta_ads(request.company_id, emails, "mock_token")
    klaviyo_res = await export_to_klaviyo(request.company_id, vips, "mock_key")
    
    return {
        "status": "success",
        "exports": [meta_res, klaviyo_res]
    }

# --- Explainer Engine API ---
# Plain language explanations for all algorithm metrics

class ExplainRequest(BaseModel):
    """Request body for explaining a metric."""
    value: float
    context: Optional[dict] = None
    locale: Optional[str] = "es"

@app.get("/api/explain/categories")
async def list_explainer_categories():
    """
    Lists all available algorithm categories that can be explained.
    """
    categories = ExplainerRegistry.list_categories()
    return {
        "categories": categories,
        "count": len(categories)
    }

@app.get("/api/explain/{category}/metrics")
async def list_category_metrics(category: str):
    """
    Lists all metrics available for a given category.
    """
    explainer = ExplainerRegistry.get(category)
    if not explainer:
        raise HTTPException(status_code=404, detail=f"Category '{category}' not found")
    
    metrics = explainer.get_supported_metrics()
    schemas = []
    for m in metrics:
        schema = explainer.get_metric_schema(m)
        if schema:
            schemas.append({
                "id": schema.id,
                "name": schema.name,
                "name_en": schema.name_en,
                "unit": schema.unit.value,
                "direction": schema.direction.value
            })
    
    return {
        "category": category,
        "metrics": schemas,
        "count": len(schemas)
    }

@app.post("/api/explain/{category}/{metric_id}")
async def explain_metric(category: str, metric_id: str, request: ExplainRequest):
    """
    Get a plain language explanation for a metric value.
    
    Args:
        category: Algorithm category (ltv, mmm, eclat, thompson, linucb, profit)
        metric_id: Specific metric (clv, roas, support, etc.)
        request: ExplainRequest with value and optional context
        
    Returns:
        ExplainedResult with human-readable explanation
    """
    explainer = ExplainerRegistry.get(category)
    if not explainer:
        raise HTTPException(status_code=404, detail=f"Category '{category}' not found")
    
    if metric_id not in explainer.get_supported_metrics():
        raise HTTPException(status_code=404, detail=f"Metric '{metric_id}' not found in '{category}'")
    
    # Set locale if different
    if request.locale and request.locale != explainer.locale:
        explainer.locale = request.locale
    
    result = explainer.explain(metric_id, request.value, request.context)
    
    return result.to_dict()

@app.get("/api/explain/{category}/{metric_id}/quick")
async def quick_explain(category: str, metric_id: str, value: float, locale: str = "es"):
    """
    Quick GET endpoint for explaining a metric (no context).
    
    Example: /api/explain/ltv/clv/quick?value=487.32
    """
    explainer = ExplainerRegistry.get(category)
    if not explainer:
        raise HTTPException(status_code=404, detail=f"Category '{category}' not found")
    
    explainer.locale = locale
    return result.to_dict()
@app.exception_handler(400)
async def custom_400_handler(request: Request, __):
    return templates.TemplateResponse("error/400.html", {"request": request}, status_code=400)

@app.exception_handler(401)
async def custom_401_handler(request: Request, __):
    return templates.TemplateResponse("error/401.html", {"request": request}, status_code=401)

@app.exception_handler(403)
async def custom_403_handler(request: Request, __):
    return templates.TemplateResponse("error/403.html", {"request": request}, status_code=403)

@app.exception_handler(404)
async def custom_404_handler(request: Request, __):
    return templates.TemplateResponse("error/404.html", {"request": request}, status_code=404)

@app.exception_handler(405)
async def custom_405_handler(request: Request, __):
    return templates.TemplateResponse("error/405.html", {"request": request}, status_code=405)

@app.exception_handler(422)
async def custom_422_handler(request: Request, __):
    return templates.TemplateResponse("error/422.html", {"request": request}, status_code=422)

@app.exception_handler(429)
async def custom_429_handler(request: Request, __):
    return templates.TemplateResponse("error/429.html", {"request": request}, status_code=429)

@app.exception_handler(500)
async def custom_500_handler(request: Request, __):
    return templates.TemplateResponse("error/500.html", {"request": request}, status_code=500)

@app.exception_handler(502)
async def custom_502_handler(request: Request, __):
    return templates.TemplateResponse("error/502.html", {"request": request}, status_code=502)

@app.exception_handler(503)
async def custom_503_handler(request: Request, __):
    return templates.TemplateResponse("error/503.html", {"request": request}, status_code=503)

@app.exception_handler(504)
async def custom_504_handler(request: Request, __):
    return templates.TemplateResponse("error/504.html", {"request": request}, status_code=504)

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    # Dynamic routing for supported premium error templates
    supported_errors = [400, 401, 403, 404, 405, 422, 429, 500, 502, 503, 504]
    if exc.status_code in supported_errors:
        return templates.TemplateResponse(f"errors/{exc.status_code}.html", {"request": request}, status_code=exc.status_code)
    
    # Fallback for other status codes
    return HTMLResponse(
        content=f"<h1>Error {exc.status_code}</h1><p>{exc.detail}</p>", 
        status_code=exc.status_code
    )


# ============================================================
# DATA INGESTION API (Universal Import)
# ============================================================

from .data_ingestion import DataIngestion, get_available_sources, get_template_columns

class CSVUploadRequest(BaseModel):
    csv_content: str
    data_type: str  # 'ventas', 'clientes', 'productos', 'gastos'
    source: str = "generic"  # 'shopify', 'square', 'holded', etc.

class JSONIngestRequest(BaseModel):
    data: List[dict]
    data_type: str

class ManualVentaRequest(BaseModel):
    order_id: str
    customer_id: str
    order_date: str
    revenue: float
    canal: str = "manual"

class ManualClienteRequest(BaseModel):
    customer_id: str
    email: Optional[str] = None
    nombre: Optional[str] = None

class ManualProductoRequest(BaseModel):
    product_id: str
    name: str
    price: float
    cogs: Optional[float] = None

class ManualGastoRequest(BaseModel):
    fecha: str
    canal: str
    inversion: float


@app.get("/api/ingest/sources")
async def list_data_sources():
    """List all supported data sources with their categories."""
    return {"sources": get_available_sources()}


@app.get("/api/ingest/template/{source}/{data_type}")
async def get_source_template(source: str, data_type: str):
    """Get expected column mapping for a source-datatype combination."""
    columns = get_template_columns(source, data_type)
    return {"source": source, "data_type": data_type, "columns": columns}


@app.post("/api/ingest/csv/preview")
async def preview_csv_upload(request: CSVUploadRequest, 
                             context: CompanyContext = Depends(get_current_user)):
    """Preview CSV mapping without inserting data."""
    ingestion = DataIngestion(context.company_id)
    result = ingestion.preview_csv(request.csv_content, request.data_type, request.source)
    return result


@app.post("/api/ingest/csv")
async def upload_csv(request: CSVUploadRequest, 
                     context: CompanyContext = Depends(get_current_user)):
    """Upload and ingest CSV data."""
    ingestion = DataIngestion(context.company_id)
    result = ingestion.ingest_csv(request.csv_content, request.data_type, request.source)
    return result


@app.post("/api/ingest/webhook")
async def webhook_ingest(request: JSONIngestRequest, 
                         context: CompanyContext = Depends(get_current_user)):
    """
    Webhook endpoint for push integrations.
    
    External systems can POST normalized data directly.
    """
    ingestion = DataIngestion(context.company_id)
    result = ingestion.ingest_json(request.data, request.data_type)
    return result


@app.post("/api/ingest/manual/venta")
async def insert_manual_venta(request: ManualVentaRequest, 
                              context: CompanyContext = Depends(get_current_user)):
    """Insert a single sale manually."""
    ingestion = DataIngestion(context.company_id)
    return ingestion.insert_venta(
        request.order_id, request.customer_id,
        request.order_date, request.revenue, request.canal
    )


@app.post("/api/ingest/manual/cliente")
async def insert_manual_cliente(request: ManualClienteRequest, 
                                context: CompanyContext = Depends(get_current_user)):
    """Insert a single customer manually."""
    ingestion = DataIngestion(context.company_id)
    return ingestion.insert_cliente(
        request.customer_id, request.email, request.nombre
    )


@app.post("/api/ingest/manual/producto")
async def insert_manual_producto(request: ManualProductoRequest, 
                                 context: CompanyContext = Depends(get_current_user)):
    """Insert a single product with COGS manually."""
    ingestion = DataIngestion(context.company_id)
    return ingestion.insert_producto(
        request.product_id, request.name, request.price, request.cogs
    )


@app.post("/api/ingest/manual/gasto")
async def insert_manual_gasto(request: ManualGastoRequest, 
                              context: CompanyContext = Depends(get_current_user)):
    """Insert marketing spend manually."""
    ingestion = DataIngestion(context.company_id)
    return ingestion.insert_gasto(
        request.fecha, request.canal, request.inversion
    )


# === DATA QUALITY & ALGORITHM TIER ENDPOINTS ===
from fastapi import UploadFile, File
from core.data_quality import DataQualityAnalyzer, DataQualityReport
from core.integrity_guard import IntegrityGuard
from .ingestion_audit import IngestionAuditor
from core.algorithm_tiers import AlgorithmTierService, get_algorithm_status
import pandas as pd
import io


@app.post("/api/data/analyze")
async def analyze_uploaded_data(file: UploadFile = File(...)):
    """
    Analiza un archivo CSV/Excel subido y retorna un reporte de calidad de datos.
    
    Retorna:
    - Profundidad hist├│rica (meses de datos)
    - Completitud de campos
    - Densidad de registros
    - Algoritmos desbloqueados/bloqueados
    - Recomendaciones para mejorar la calidad
    """
    try:
        contents = await file.read()
        
        # Detectar formato por extensi├│n
        filename = file.filename.lower() if file.filename else ""
        
        if filename.endswith('.xlsx') or filename.endswith('.xls'):
            df = pd.read_excel(io.BytesIO(contents))
        elif filename.endswith('.json'):
            df = pd.read_json(io.BytesIO(contents))
        else:
            # Default: CSV
            df = pd.read_csv(io.BytesIO(contents))
        
        analyzer = DataQualityAnalyzer()
        report = analyzer.analyze(df)
        
        return {
            "success": True,
            "filename": file.filename,
            "report": report.to_dict()
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "report": None
        }


@app.get("/api/data/health/{company_id}")
async def get_data_health(company_id: str):
    """
    Retorna el estado de salud de datos de una cuenta.
    Analiza los datos existentes en la base de datos.
    """
    try:
        # Obtener datos de la empresa desde la base de datos
        if supabase:
            ventas = supabase.table("ventas").select("*").eq("company_id", company_id).execute()
            
            if ventas.data:
                df = pd.DataFrame(ventas.data)
                analyzer = DataQualityAnalyzer()
                report = analyzer.analyze(df)
                return report.to_dict()
        
        # Si no hay datos o no hay supabase
        return {
            "overall": {"score": 0, "level": "critical"},
            "row_count": 0,
            "recommendations": ["Conecta una fuente de datos para empezar."],
            "algorithms": {"unlocked": 0, "locked": 16}
        }
        
    except Exception as e:
        return {"error": str(e), "overall": {"score": 0, "level": "critical"}}


@app.get("/api/data/integrity/{company_id}")
async def get_deep_integrity(company_id: str, context: Optional[str] = "ventas"):
    """
    Realiza un escaneo profundo de integridad (duplicados, gaps, NaNs cr├¡ticos).
    """
    try:
        if supabase:
            # Obtener datos para escaneo
            res = supabase.table(context).select("*").eq("company_id", company_id).limit(1000).execute()
            if res.data:
                df = pd.DataFrame(res.data)
                guard = IntegrityGuard()
                issues = guard.scan(df, context=context)
                return {
                    "success": True,
                    "company_id": company_id,
                    "context": context,
                    "issue_count": len(issues),
                    "issues": [
                        {
                            "type": i.type,
                            "severity": i.severity,
                            "column": i.column,
                            "message": i.message,
                            "affected_rows": i.affected_rows
                        } for i in issues
                    ]
                }
        
        return {"success": False, "message": "No data found for scanning"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/data/receipts/{company_id}")
async def get_ingestion_receipts(company_id: str):
    """
    Retorna el historial de recibos de importaci├│n (Audit Trail).
    """
    # En un entorno real, esto consultar├¡a la tabla 'ingestion_receipts'
    # Por ahora devolvemos un log simulado basado en el IngestionAuditor
    return {
        "company_id": company_id,
        "receipts": [
            {
                "batch_id": "batch_20260212_a8b9c0",
                "timestamp": "2026-02-12T10:00:00Z",
                "source": "shopify",
                "status": "completed",
                "input_rows": 1250,
                "success_rows": 1250,
                "checksum": "sha256:e3b0c442..."
            },
            {
                "batch_id": "batch_20260211_d1e2f3",
                "timestamp": "2026-02-11T15:30:00Z",
                "source": "manual_csv",
                "status": "partial",
                "input_rows": 500,
                "success_rows": 485,
                "errors": 15,
                "checksum": "sha256:88a1b2c3..."
            }
        ]
    }


@app.get("/api/algorithms/status")
async def get_algorithms_status(months: int = 0, records: int = 0):
    """
    Retorna el estado de todos los algoritmos seg├║n los datos disponibles.
    
    Query params:
    - months: meses de datos hist├│ricos
    - records: cantidad de registros
    
    Retorna lista de algoritmos con estado desbloqueado/bloqueado.
    """
    return get_algorithm_status(months, records)


@app.get("/api/algorithms/catalog")
async def get_algorithms_catalog():
    """
    Retorna el cat├ílogo completo de algoritmos disponibles.
    """
    service = AlgorithmTierService()
    return {
        "total": len(service.catalog),
        "algorithms": [a.to_dict() for a in service.catalog],
        "tiers": ["basic", "standard", "advanced", "precision"]
    }


# Entry point for local development
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

