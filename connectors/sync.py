"""
Unified Sync Hub v3.0 - Tactics (SOTA Async Ingestion)
Consolidates all external API connectors into a high-concurrency asynchronous layer.
Targeting the 'Golden Triangle': Spend (Ads), Revenue (Sales), and Sentiment (Support).
"""

import asyncio
import logging
import time
from typing import Dict, List, Any, Optional, Type
from abc import ABC, abstractmethod
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("tactics.sync")

# ============================================================
# ASYNC SYNC PROVIDER INTERFACE
# ============================================================

class AsyncSyncProvider(ABC):
    """
    Base class for all asynchronous data providers.
    """
    def __init__(self, provider_id: str, credentials: Dict[str, Any]):
        self.provider_id = provider_id
        self.credentials = credentials
        self.client = httpx.AsyncClient(timeout=30.0)

    @abstractmethod
    async def authenticate(self) -> bool:
        """Authenticates with the provider API."""
        pass

    @abstractmethod
    async def fetch_data(self, company_id: str, days: int = 30) -> List[Dict[str, Any]]:
        """Fetches raw data from the provider."""
        pass

    async def close(self):
        """Closes the HTTP client."""
        await self.client.aclose()

# ============================================================
# UNIFIED SYNC HUB (ASYNC)
# ============================================================

from .meta_ads import MetaAdsConnector
from .google_ads import GoogleAdsConnector
from .sentiment import SentimentConnector
from .pos_retail import POSRetailConnector
from core.supabase_bridge import SupabaseBridge

class UnifiedSyncHub:
    """
    SOTA Async Router for multi-source business intelligence ingestion.
    """
    def __init__(self, supabase_url: Optional[str] = None, supabase_key: Optional[str] = None):
        self.providers: Dict[str, Type[AsyncSyncProvider]] = {
            "meta": MetaAdsConnector,
            "google": GoogleAdsConnector,
            "sentiment": SentimentConnector,
            "pos": POSRetailConnector
        }
        self.storage = SupabaseBridge(url=supabase_url, key=supabase_key)
        self.active_tasks = []

    def register_provider(self, provider_id: str, provider_class: Type[AsyncSyncProvider]):
        """Registers a new data provider (Meta, Google, Shopify, etc.)"""
        self.providers[provider_id] = provider_class
        logger.info(f"Provider registered: {provider_id}")

    async def sync_company(self, company_id: str, credentials_map: Dict[str, Dict[str, Any]], days: int = 30):
        """
        Orchestrates full company data sync in parallel.
        This is the SOTA ingestion core.
        """
        start_time = time.time()
        logger.info(f"Starting async sync for company: {company_id}")

        sync_tasks = []
        provider_instances = []

        for provider_id, creds in credentials_map.items():
            if provider_id in self.providers:
                # Instantiate provider
                provider_class = self.providers[provider_id]
                instance = provider_class(provider_id, creds)
                provider_instances.append(instance)
                
                # Add task
                sync_tasks.append(self._run_single_sync(company_id, instance, days))
            else:
                logger.warning(f"Provider {provider_id} not found in registry.")

        # Execute all syncs in parallel
        results = await asyncio.gather(*sync_tasks, return_exceptions=True)
        
        # Cleanup
        for instance in provider_instances:
            await instance.close()

        duration = time.time() - start_time
        logger.info(f"Sync completed in {duration:.2f} seconds.")
        
        return dict(zip(credentials_map.keys(), results))

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def _run_single_sync(self, company_id: str, provider: AsyncSyncProvider, days: int):
        """Runs a single provider sync with retry logic and persistence."""
        try:
            is_auth = await provider.authenticate()
            if not is_auth:
                return {"status": "error", "message": "Authentication failed"}

            data = await provider.fetch_data(company_id, days)
            
            # Persist to Supabase Hybrid Storage (JSONB Payload)
            persisted = self.storage.upsert_raw_payload(company_id, provider.provider_id, data)

            return {
                "status": "success" if persisted else "warning", 
                "records": len(data),
                "persisted": persisted
            }
        except Exception as e:
            logger.error(f"Sync error for {provider.provider_id}: {e}")
            raise e
