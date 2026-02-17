import os
import time
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from api.routers import pages, analytics, sync, webhooks

app = FastAPI(
    title="Tactics AI API",
    description="Resilient Business Intelligence & Data Science Platform",
    version="2.0.0"
)

# --- Middleware ---
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "https://tactics.ai").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

# --- Static Files ---
app.mount("/static", StaticFiles(directory="static"), name="static")

# --- Specific Routes (Prioritized to avoid conflict) ---

@app.get("/health")
async def health():
    """System health check endpoint."""
    return {"status": "healthy", "timestamp": time.time()}

# --- Include Routers ---

# API Routes first
app.include_router(analytics.router)
app.include_router(sync.router)
app.include_router(webhooks.router)

# Page Routes last (contains catch-all /{locale})
app.include_router(pages.router)

# --- Error Handlers ---

@app.exception_handler(404)
async def custom_404_handler(request: Request, __):
    return JSONResponse(
        status_code=404,
        content={"error": "Not Found", "path": request.url.path}
    )

@app.exception_handler(500)
async def custom_500_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"error": "Internal Server Error", "detail": str(exc)}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)
