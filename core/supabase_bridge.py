"""
Supabase Bridge - Tactics
SOTA Hybrid Storage Layer (PostgreSQL + JSONB).
"""

import logging
from typing import Dict, List, Any, Optional
from supabase import create_client, Client
from .config import ALGORITHM_CONFIG

logger = logging.getLogger("tactics.core.supabase")

class SupabaseBridge:
    """
    Interface for Managed Hybrid Storage on Supabase.
    Bridges relational SQL integrity with NoSQL JSONB flexibility.
    """
    
    def __init__(self, url: Optional[str] = None, key: Optional[str] = None):
        config = ALGORITHM_CONFIG.get("supabase", {})
        self.url = url or config.get("url")
        self.key = key or config.get("key")
        self.tables = config.get("tables", {})
        
        if self.url and self.key:
            try:
                self.client: Client = create_client(self.url, self.key)
                logger.info("Supabase connected successfully.")
            except Exception as e:
                logger.error(f"Supabase connection failed: {e}")
                self.client = None
        else:
            logger.warning("Supabase credentials missing. Running in disconnected mode.")
            self.client = None

    def upsert_raw_payload(self, company_id: str, provider_id: str, payload: List[Dict]):
        """
        Stores raw data in JSONB column. 
        SOTA: Preserves the source truth for audit and future re-parsing.
        """
        if not self.client:
            return False
            
        data = {
            "company_id": company_id,
            "provider_id": provider_id,
            "payload": payload,
            "ingested_at": "now()"
        }
        
        try:
            table = self.tables.get("ingestion_raw", "raw_payloads")
            response = self.client.table(table).upsert(data).execute()
            return True
        except Exception as e:
            logger.error(f"Supabase upsert failed: {e}")
            return False

    def get_company_data(self, company_id: str, table_key: str):
        """Retrieves structured data for a specific company."""
        if not self.client:
            return []
            
        try:
            table_name = self.tables.get(table_key)
            if not table_name:
                return []
                
            response = self.client.table(table_name).select("*").eq("company_id", company_id).execute()
            return response.data
        except Exception as e:
            logger.error(f"Error fetching data from Supabase: {e}")
            return []

    # SOTA: Real-time signals and Vector search methods
    def get_sentiment_summary(self, company_id: str):
        """Placeholder for pgvector/sentiment analysis."""
        table = self.tables.get("sentiment_signals")
        # Logic to query sentiment trends...
        pass
