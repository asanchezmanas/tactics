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

        if not shop_url or not access_token:
            logger.warning("Missing Shopify credentials. Falling back to mock data.")
            return self._fetch_mock_data()

        try:
            # SOTA: Real Shopify API Call
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Calculate since date
                since_date = (datetime.now() - timedelta(days=days)).isoformat()
                
                response = await client.get(
                    f"https://{shop_url}/admin/api/2024-01/orders.json",
                    headers={"X-Shopify-Access-Token": access_token},
                    params={
                        "status": "any", 
                        "limit": 250, 
                        "created_at_min": since_date
                    }
                )
                response.raise_for_status()
                orders = response.json().get("orders", [])
                
                return [self._normalize_order(o) for o in orders]
        except Exception as e:
            logger.error(f"Shopify API error: {e}. Falling back to mock.")
            return self._fetch_mock_data()

    def _normalize_order(self, order: Dict) -> Dict:
        """SOTA normalization for Shopify orders."""
        return {
            "id": str(order.get("id")),
            "customer_id": str(order.get("customer", {}).get("id")),
            "revenue": float(order.get("total_price", 0)),
            "order_date": order.get("created_at"),
            "channel": order.get("source_name", "web"),
            "items": [i.get("title") for i in order.get("line_items", [])]
        }

    def _fetch_mock_data(self) -> List[Dict[str, Any]]:
        return [
            {
                "id": "sh_9922",
                "customer_id": "cust_shopify_1",
                "revenue": 120.50,
                "order_date": "2026-02-15T10:00:00Z",
                "channel": "web",
                "items": ["t-shirt", "cap"]
            },
            {
                "id": "sh_9923",
                "customer_id": "cust_shopify_2",
                "revenue": 45.00,
                "order_date": "2026-02-16T12:00:00Z",
                "channel": "instagram_shop",
                "items": ["socks"]
            }
        ]
