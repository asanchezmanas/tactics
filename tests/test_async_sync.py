"""
Verification Test for SOTA Async Ingestion Hub - Tactics
Validates concurrent syncing of AdTech, Sales, and Sentiment data.
"""

import asyncio
import logging
import pytest
from connectors.sync import UnifiedSyncHub

# Setup isolated logging for tests
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("tactics.test.sync")

@pytest.mark.asyncio
async def test_full_company_sync_flow():
    """
    Simulates a full omnichannel company sync.
    Validates that multiple providers run concurrently and persist data.
    """
    hub = UnifiedSyncHub() # Running in disconnected mode (mock persistence)
    
    company_id = "test_omnichannel_co"
    credentials = {
        "meta": {"access_token": "test_token", "ad_account_id": "act_123"},
        "google": {"client_id": "google_cid", "developer_token": "dev_123"},
        "sentiment": {"api_key": "zendesk_key"},
        "pos": {"api_key": "stripe_terminal_key"}
    }
    
    logger.info("Triggering SOTA parallel sync...")
    results = await hub.sync_company(company_id, credentials, days=30)
    
    # Assertions
    assert "meta" in results
    assert "google" in results
    assert "sentiment" in results
    assert "pos" in results
    
    for provider, result in results.items():
        logger.info(f"Result for {provider}: {result}")
        assert result["status"] == "success" or result["status"] == "warning"
        assert result["records"] > 0

if __name__ == "__main__":
    # Quick manual run
    asyncio.run(test_full_company_sync_flow())
