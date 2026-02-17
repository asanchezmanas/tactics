"""
Shopify Connector - Tactics
Async ingestion for Sales and Customer data.
"""

import logging
from typing import List, Dict, Any
from .sync import AsyncSyncProvider

logger = logging.getLogger("tactics.connectors.shopify")

class ShopifyConnector(AsyncSyncProvider):
    """
    SOTA Async Connector for Shopify Admin API.
    """
    
    async def authenticate(self) -> bool:
        return "access_token" in self.credentials and "shop_url" in self.credentials

    async def fetch_data(self, company_id: str, days: int = 30) -> List[Dict[str, Any]]:
        logger.info(f"Fetching Shopify data for company {company_id}")
        
        shop_url = self.credentials.get("shop_url")
        access_token = self.credentials.get("access_token")
        
        # SOTA logic: In a real environment, we'd use httpx to fetch from /admin/api/...
        # For the marathon, we mock the SOTA response format
        return [
            {
                "id": "sh_9922",
                "customer_id": "cust_shopify_1",
                "revenue": 120.50,
                "order_date": "2026-02-15T10:00:00Z",
                "Source name": "web", # This maps to canal_origen in DataIngestion
                "items": ["t-shirt", "cap"]
            },
            {
                "id": "sh_9923",
                "customer_id": "cust_shopify_2",
                "revenue": 45.00,
                "order_date": "2026-02-16T12:00:00Z",
                "source_name": "instagram_shop",
                "items": ["socks"]
            }
        ]
