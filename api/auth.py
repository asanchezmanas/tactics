import os
import sys
import json
import base64
from datetime import datetime

# Add project root to path
sys.path.append(os.getcwd())

from pydantic import BaseModel
from fastapi import Request, Depends, HTTPException

class CompanyContext(BaseModel):
    """Contextual branding and tier information for the current company."""
    company_id: str
    tier: str = "core"

async def get_current_user(request: Request) -> CompanyContext:
    """FastAPI dependency to extract company context from the request."""
    # Simulation: In production this would use JWT/Supabase auth
    # HARDENING: Only allow X-Company-ID header, no query params or fallback
    company_id = request.headers.get("X-Company-ID")
    if not company_id:
        raise HTTPException(status_code=401, detail="X-Company-ID header required")
    
    # In a real app, we'd fetch the tier from the DB here
    # For now, we mock a tier based on the ID for demonstration purposes
    tier = "enterprise" if "ent" in company_id.lower() else "core"
    return CompanyContext(company_id=company_id, tier=tier)

def require_tier(tier: str):
    """Dependency factory to gate routes by company tier."""
    def dependency(context: CompanyContext = Depends(get_current_user)):
        # HARDENING: Actually check the tier
        tier_levels = {"core": 0, "standard": 1, "enterprise": 2, "precision": 3}
        current_level = tier_levels.get(context.tier, 0)
        required_level = tier_levels.get(tier, 0)
        
        if current_level < required_level:
            raise HTTPException(
                status_code=403, 
                detail=f"Tier '{tier}' required (current: '{context.tier}')"
            )
        return context
    return dependency

from api.database import encrypt_token as _encrypt_token, decrypt_token as _decrypt_token, get_local_cache
from api.pipeline import run_full_pipeline, PipelineTier
from core.secure_vault import SecureVault
if __name__ == "__main__":
    asyncio.run(main())
