from fastapi import APIRouter, Depends, BackgroundTasks
from api.auth import CompanyContext, require_tier
from api.pipeline import run_full_pipeline, PipelineTier
from api.database import process_retry_queue

router = APIRouter(prefix="/api/v1/sync")

@router.get("/all")
async def trigger_full_sync(
    background_tasks: BackgroundTasks,
    context: CompanyContext = Depends(require_tier("standard"))
):
    """Triggers a full data pipeline sync in the background."""
    tier = PipelineTier.ENTERPRISE if context.tier == "enterprise" else PipelineTier.CORE
    background_tasks.add_task(run_full_pipeline, context.company_id, tier)
    return {"status": "accepted", "message": f"Sync started for {context.company_id}"}

@router.get("/retry")
async def process_retries(context: CompanyContext = Depends(require_tier("enterprise"))):
    """Manually triggers processing of the retry queue."""
    process_retry_queue()
    return {"status": "success"}
