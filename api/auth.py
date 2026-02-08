import os
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from pydantic import BaseModel
from typing import Optional

try:
    from .database import supabase
except ImportError:
    supabase = None

# Using HTTPBearer for Bearer token extraction
security = HTTPBearer()

# Supabase JWT Configuration
# These usually come from Supabase environment
SUPABASE_JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET")  # Required for local decoding
SUPABASE_ALGORITHM = "HS256"

class CompanyContext(BaseModel):
    company_id: str
    user_id: str
    tier: str = "core"
    email: Optional[str] = None

async def get_current_user(auth: HTTPAuthorizationCredentials = Depends(security)) -> CompanyContext:
    """
    FastAPI dependency to verify Supabase JWT and inject company context.
    """
    if not supabase:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection not available"
        )

    token = auth.credentials
    
    try:
        # 1. Verify and decode JWT
        # NOTE: Ideally we use supabase.auth.get_user(token) for remote verification,
        # or jwt.decode if we have the secret for local performance.
        # We'll use the client for maximum reliability with Supabase features.
        user_res = supabase.auth.get_user(token)
        if not user_res or not user_res.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token"
            )
        
        user = user_res.user
        
        # 2. Extract Company ID from JWT claims (preferred) or metadata
        # Supabase allows custom claims via PostgreSQL functions, often mapped to app_metadata
        company_id = user.app_metadata.get("company_id")
        
        if not company_id:
            # Fallback: Query the database for the user's company (if not in JWT)
            # This is slower but safer for initial setup
            res = supabase.table("user_profiles").select("company_id").eq("id", user.id).execute()
            if res.data:
                company_id = res.data[0].get("company_id")
        
        if not company_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User not associated with any company"
            )

        # 3. Fetch Company Tier
        # We cache this in production, but for now we query
        comp_res = supabase.table("companies").select("tier").eq("id", company_id).execute()
        tier = "core"
        if comp_res.data:
            tier = comp_res.data[0].get("tier", "core")

        return CompanyContext(
            company_id=company_id,
            user_id=user.id,
            tier=tier,
            email=user.email
        )

    except Exception as e:
        print(f"[AUTH] Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )

def require_tier(required_tier: str):
    """
    Dependency factory to enforce tier-based access.
    Usage: Depends(require_tier("enterprise"))
    """
    async def tier_checker(context: CompanyContext = Depends(get_current_user)):
        if required_tier == "enterprise" and context.tier != "enterprise":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"This feature requires an {required_tier} plan"
            )
        return context
    return tier_checker
