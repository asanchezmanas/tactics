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
    """FastAPI dependency to extract company context from Supabase."""
    company_id = request.headers.get("X-Company-ID")
    if not company_id:
        raise HTTPException(status_code=401, detail="X-Company-ID header required")
    
    from api.database import db_bridge
    if not db_bridge.client:
        # Fallback for development if Supabase not configured
        tier = "PRECISION" if "ent" in company_id.lower() else "INTELLIGENCE"
        return CompanyContext(company_id=company_id, tier=tier)

    try:
        res = db_bridge.client.table("companies").select("tier").eq("id", company_id).single().execute()
        if not res.data:
            raise HTTPException(status_code=403, detail="Company not found in registry")
        return CompanyContext(company_id=company_id, tier=res.data["tier"].upper())
    except Exception as e:
        # Graceful fallback or rejection based on configuration
        raise HTTPException(status_code=401, detail=f"Auth failure: {str(e)}")

def require_tier(tier: str):
    """Dependency factory to gate routes by company tier."""
    def dependency(context: CompanyContext = Depends(get_current_user)):
        tier_levels = {"INTELLIGENCE": 0, "OPTIMISATION": 1, "PRECISION": 2}
        current_level = tier_levels.get(context.tier, 0)
        required_level = tier_levels.get(tier.upper(), 0)
        
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
