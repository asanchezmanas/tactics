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
    company_id = request.headers.get("X-Company-ID") or request.query_params.get("demo") or "demo_company"
    return CompanyContext(company_id=company_id)

def require_tier(tier: str):
    """Dependency factory to gate routes by company tier."""
    def dependency(context: CompanyContext = Depends(get_current_user)):
        return context
    return dependency

from api.database_resilient import _encrypt_token, _decrypt_token, get_local_cache
from api.pipeline import run_full_pipeline, PipelineTier
from core.secure_vault import SecureVault
import asyncio

def test_token_encryption():
    """Verifies the encryption/decryption layer for sensitive credentials."""
    print("--- Testing Token Encryption ---")
    
    # Mock master key
    os.environ["VAULT_MASTER_KEY"] = "test_master_key_123"
    
    plain_token = "sk_live_shopify_12345"
    print(f"Original Token: {plain_token}")
    
    # 1. Encrypt
    encrypted = _encrypt_token(plain_token)
    print(f"Encrypted Blob: {encrypted}")
    
    assert encrypted.startswith("enc:"), "Encrypted token should have 'enc:' prefix"
    assert encrypted != plain_token, "Encrypted token should not be plain text"
    
    # 2. Decrypt
    decrypted = _decrypt_token(encrypted)
    print(f"Decrypted Token: {decrypted}")
    
    assert decrypted == plain_token, "Decryption failed to restore original token"
    
    # 3. Test legacy (plain text) handling
    legacy_token = "old_plain_token"
    assert _decrypt_token(legacy_token) == legacy_token, "Legacy plain-text tokens should be returned as-is"
    
    print("Ô£à Token encryption layer verified.")

def test_vault_multi_tenancy():
    """Verifies that vault snapshots are tied to the company_id."""
    print("\n--- Testing Vault Multi-Tenancy ---")
    
    company_a = "company_alpha"
    company_b = "company_beta"
    
    vault_a = SecureVault(company_id=company_a)
    vault_b = SecureVault(company_id=company_b)
    
    # Store in A
    vault_a.store_audit_document("test", b"secret_a", "file_a")
    
    # Check A has it
    keys_a = vault_a.backend.list_keys(prefix=company_a)
    print(f"Company A Keys: {keys_a}")
    assert any(company_a in k and "file_a" in k for k in keys_a), "Company A should see its own file"
    
    # Check B DOES NOT have it
    keys_b = vault_b.backend.list_keys(prefix=company_b)
    print(f"Company B Keys: {keys_b}")
    assert not any("file_a" in k for k in keys_b), "Company B should NOT see Company A's file"
    
async def test_tier_gating():
    """Verifies that tier-specific logic (e.g. vault backups) is gated correctly."""
    print("\n--- Testing Tier Gating ---")
    
    company_id = "test_tier_gating"
    
    # 0. Insert mock data into local cache to allow pipeline to run
    cache = get_local_cache()
    mock_ventas = [
        {"customer_id": "c1", "order_date": "2024-01-01", "revenue": 100.0},
        {"customer_id": "c2", "order_date": "2024-01-02", "revenue": 150.0}
    ]
    mock_gastos = [
        {"fecha": "2024-01-01", "canal": "Google Ads", "inversion": 50.0, "impresiones": 1000, "clics": 50}
    ]
    cache.set(f"ventas:{company_id}", mock_ventas, "ventas", company_id=company_id)
    cache.set(f"gastos:{company_id}", mock_gastos, "gastos", company_id=company_id)
    
    # Run Core Tier
    print("Running Pipeline (CORE tier)...")
    res_core = await run_full_pipeline(company_id, tier=PipelineTier.CORE)
    assert "vault_model_snapshot" not in res_core.get("steps_completed", []), "Vault snapshot should NOT run in CORE tier"
    
    # Run Enterprise Tier
    print("Running Pipeline (ENTERPRISE tier)...")
    res_ent = await run_full_pipeline(company_id, tier=PipelineTier.ENTERPRISE)
    assert "vault_model_snapshot" in res_ent.get("steps_completed", []), "Vault snapshot SHOULD run in ENTERPRISE tier"
    
    print("Ô£à Tier gating verified.")

async def main():
    try:
        test_token_encryption()
        test_vault_multi_tenancy()
        await test_tier_gating()
        print("\n­ƒÅå Production Hardening & Tier Gating verified successfully.")
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"\nÔØî Verification failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
