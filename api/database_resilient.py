"""
Resilient Database Layer for Tactics

Architecture:
- RELATIONAL: clientes, ventas, gastos_marketing (critical, structured)
- JSONB/SEMI-STRUCTURED: predictions, insights, model_metadata (flexible, fault-tolerant)
- LOCAL CACHE: SQLite fallback when Supabase is unavailable

Features:
- Graceful degradation: app works even if predictions fail
- Local cache: continues working offline
- Retry queue: failed writes are queued for later
- JSONB columns: schema-flexible for AI outputs
"""

import os
import json
import sqlite3
import base64
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, List, Any, Union
from functools import wraps
import threading
import queue

import pandas as pd
from dotenv import load_dotenv
from core.secure_vault import EncryptionManager

# Supabase with graceful fallback
try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    Client = None

load_dotenv()

# ============================================================
# CONFIGURATION
# ============================================================

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
LOCAL_CACHE_PATH = Path(os.getenv("LOCAL_CACHE_PATH", ".cache/tactics.db"))
RETRY_QUEUE_PATH = Path(os.getenv("RETRY_QUEUE_PATH", ".cache/retry_queue.json"))

# Max retries for failed operations
MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 60

# ============================================================
# SUPABASE CLIENT (SINGLETON)
# ============================================================

_supabase_client: Optional[Client] = None
_supabase_lock = threading.Lock()


def get_supabase() -> Optional[Client]:
    """Thread-safe Supabase client getter with lazy initialization."""
    global _supabase_client
    
    if not SUPABASE_AVAILABLE:
        return None
    
    if _supabase_client is None:
        with _supabase_lock:
            if _supabase_client is None and SUPABASE_URL and SUPABASE_KEY:
                try:
                    _supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
                except Exception as e:
                    print(f"[DB] Failed to initialize Supabase: {e}")
                    return None
    
    return _supabase_client


# ============================================================
# LOCAL CACHE (SQLITE)
# ============================================================

class LocalCache:
    """
    SQLite-based local cache for offline operation.
    Stores both data and failed operations for retry.
    """
    
    def __init__(self, db_path: Path = LOCAL_CACHE_PATH):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        """Initialize SQLite schema."""
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript("""
                -- Data cache table (key-value with JSON)
                CREATE TABLE IF NOT EXISTS cache (
                    cache_key TEXT PRIMARY KEY,
                    data JSON NOT NULL,
                    table_name TEXT NOT NULL,
                    company_id TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    expires_at TEXT
                );
                
                -- Retry queue for failed writes
                CREATE TABLE IF NOT EXISTS retry_queue (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    operation TEXT NOT NULL,
                    table_name TEXT NOT NULL,
                    data JSON NOT NULL,
                    error_message TEXT,
                    retry_count INTEGER DEFAULT 0,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    next_retry_at TEXT
                );
                
                -- Predictions cache (JSONB-style)
                CREATE TABLE IF NOT EXISTS predictions_cache (
                    id TEXT PRIMARY KEY,
                    company_id TEXT NOT NULL,
                    prediction_type TEXT NOT NULL,
                    input_hash TEXT,
                    output_data JSON NOT NULL,
                    confidence JSON,
                    model_version TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                );
                
                -- Index for faster lookups
                CREATE INDEX IF NOT EXISTS idx_cache_company ON cache(company_id);
                CREATE INDEX IF NOT EXISTS idx_predictions_company ON predictions_cache(company_id);
                CREATE INDEX IF NOT EXISTS idx_retry_next ON retry_queue(next_retry_at);
            """)
    
    def get(self, cache_key: str) -> Optional[Dict]:
        """Retrieve cached data."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT data, expires_at FROM cache WHERE cache_key = ?",
                (cache_key,)
            )
            row = cursor.fetchone()
            
            if row:
                data, expires_at = row
                # Check expiration
                if expires_at:
                    if datetime.fromisoformat(expires_at) < datetime.now():
                        self.delete(cache_key)
                        return None
                return json.loads(data)
        return None
    
    def set(self, cache_key: str, data: Any, table_name: str, 
            company_id: str = None, ttl_hours: int = 24):
        """Store data in cache with optional TTL."""
        expires_at = (datetime.now() + timedelta(hours=ttl_hours)).isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO cache (cache_key, data, table_name, company_id, expires_at)
                VALUES (?, ?, ?, ?, ?)
            """, (cache_key, json.dumps(data), table_name, company_id, expires_at))
    
    def delete(self, cache_key: str):
        """Remove from cache."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM cache WHERE cache_key = ?", (cache_key,))
    
    def add_to_retry_queue(self, operation: str, table_name: str, 
                           data: Dict, error_message: str):
        """Queue a failed operation for retry."""
        next_retry = (datetime.now() + timedelta(seconds=RETRY_DELAY_SECONDS)).isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO retry_queue (operation, table_name, data, error_message, next_retry_at)
                VALUES (?, ?, ?, ?, ?)
            """, (operation, table_name, json.dumps(data), error_message, next_retry))
    
    def get_pending_retries(self) -> List[Dict]:
        """Get operations ready for retry."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT id, operation, table_name, data, retry_count 
                FROM retry_queue 
                WHERE next_retry_at <= ? AND retry_count < ?
                ORDER BY created_at
            """, (datetime.now().isoformat(), MAX_RETRIES))
            
            return [
                {"id": r[0], "operation": r[1], "table_name": r[2], 
                 "data": json.loads(r[3]), "retry_count": r[4]}
                for r in cursor.fetchall()
            ]

    def get_dead_letters(self) -> List[Dict]:
        """Get operations that have exceeded max retries (Dead Letters)."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT id, operation, table_name, data, retry_count, error_message, created_at
                FROM retry_queue 
                WHERE retry_count >= ?
                ORDER BY created_at DESC
            """, (MAX_RETRIES,))
            
            return [
                {
                    "id": r[0], 
                    "operation": r[1], 
                    "table_name": r[2], 
                    "data": json.loads(r[3]), 
                    "retry_count": r[4],
                    "error": r[5],
                    "created_at": r[6]
                }
                for r in cursor.fetchall()
            ]
    
    def mark_retry_success(self, retry_id: int):
        """Remove from queue after successful retry."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM retry_queue WHERE id = ?", (retry_id,))
    
    def mark_retry_failed(self, retry_id: int):
        """Increment retry count and schedule next attempt."""
        next_retry = (datetime.now() + timedelta(seconds=RETRY_DELAY_SECONDS * 2)).isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                UPDATE retry_queue 
                SET retry_count = retry_count + 1, next_retry_at = ?
                WHERE id = ?
            """, (next_retry, retry_id))
    
    def save_prediction(self, company_id: str, prediction_type: str,
                        output_data: Dict, input_data: Dict = None,
                        confidence: Dict = None, model_version: str = None):
        """Save prediction result with JSONB-style flexibility."""
        # Create deterministic ID from company + type + optional input hash
        input_hash = None
        if input_data:
            input_hash = hashlib.md5(json.dumps(input_data, sort_keys=True).encode()).hexdigest()[:16]
        
        pred_id = f"{company_id}:{prediction_type}:{input_hash or 'latest'}"
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO predictions_cache 
                (id, company_id, prediction_type, input_hash, output_data, confidence, model_version, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                pred_id, company_id, prediction_type, input_hash,
                json.dumps(output_data),
                json.dumps(confidence) if confidence else None,
                model_version,
                datetime.now().isoformat()
            ))
    
    def get_prediction(self, company_id: str, prediction_type: str,
                       input_data: Dict = None) -> Optional[Dict]:
        """Retrieve cached prediction."""
        input_hash = None
        if input_data:
            input_hash = hashlib.md5(json.dumps(input_data, sort_keys=True).encode()).hexdigest()[:16]
        
        pred_id = f"{company_id}:{prediction_type}:{input_hash or 'latest'}"
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT output_data, confidence, model_version, created_at
                FROM predictions_cache WHERE id = ?
            """, (pred_id,))
            
            row = cursor.fetchone()
            if row:
                return {
                    "output": json.loads(row[0]),
                    "confidence": json.loads(row[1]) if row[1] else None,
                    "model_version": row[2],
                    "cached_at": row[3]
                }
        return None


# Global cache instance
_local_cache: Optional[LocalCache] = None


def get_local_cache() -> LocalCache:
    """Get or create local cache instance."""
    global _local_cache
    if _local_cache is None:
        _local_cache = LocalCache()
    return _local_cache


# ============================================================
# RESILIENT DATABASE OPERATIONS
# ============================================================

def with_fallback(cache_key_fn=None, ttl_hours: int = 24):
    """
    Decorator that adds local cache fallback to database operations.
    
    Usage:
        @with_fallback(cache_key_fn=lambda company_id: f"ventas:{company_id}")
        def get_ventas(company_id: str) -> pd.DataFrame:
            ...
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache = get_local_cache()
            
            # Generate cache key
            cache_key = None
            if cache_key_fn:
                cache_key = cache_key_fn(*args, **kwargs)
            
            # Try Supabase first
            try:
                result = func(*args, **kwargs)
                
                # Cache successful result
                if cache_key and result is not None:
                    if isinstance(result, pd.DataFrame):
                        cache.set(cache_key, result.to_dict('records'), 
                                  func.__name__, ttl_hours=ttl_hours)
                    else:
                        cache.set(cache_key, result, func.__name__, ttl_hours=ttl_hours)
                
                return result
                
            except Exception as e:
                print(f"[DB] Supabase error in {func.__name__}: {e}")
                
                # Fallback to cache
                if cache_key:
                    cached = cache.get(cache_key)
                    if cached:
                        print(f"[DB] Returning cached data for {cache_key}")
                        if func.__annotations__.get('return') == pd.DataFrame:
                            return pd.DataFrame(cached)
                        return cached
                
                # Return empty/default
                return_type = func.__annotations__.get('return')
                if return_type == pd.DataFrame:
                    return pd.DataFrame()
                elif return_type == list:
                    return []
                elif return_type == dict:
                    return {}
                return None
        
        return wrapper
    return decorator


def with_retry_queue(table_name: str):
    """
    Decorator for write operations that queues failures for retry.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                print(f"[DB] Write failed for {table_name}: {e}")
                
                # Queue for retry
                cache = get_local_cache()
                
                # Extract data from args/kwargs
                data = kwargs.get('data') or (args[1] if len(args) > 1 else {})
                if isinstance(data, pd.DataFrame):
                    data = data.to_dict('records')
                
                cache.add_to_retry_queue(
                    operation=func.__name__,
                    table_name=table_name,
                    data={"args": str(args), "kwargs": str(kwargs), "payload": data},
                    error_message=str(e)
                )
                
                return False  # Indicate failure (queued for retry)
        
        return wrapper
    return decorator


# --- Encryption Helpers for Sensitive Credentials ---

def _get_encryption_manager() -> Optional[EncryptionManager]:
    """Helper to get EncryptionManager from master key."""
    master_key = os.getenv("VAULT_MASTER_KEY")
    if not master_key:
        return None
    try:
        return EncryptionManager(master_key)
    except Exception as e:
        print(f"[DB] Encryption init failed: {e}")
        return None

def _decrypt_token(encrypted_token: str) -> str:
    """Decrypts a token if it's encrypted, otherwise returns as is."""
    if not encrypted_token or not encrypted_token.startswith("enc:"):
        return encrypted_token
    
    manager = _get_encryption_manager()
    if not manager:
        return encrypted_token
        
    try:
        # Remove 'enc:' prefix and decode base64
        blob = base64.b64decode(encrypted_token[4:])
        decrypted = manager.decrypt_from_blob(blob)
        return decrypted.decode('utf-8')
    except Exception as e:
        print(f"[DB] Decryption failed: {e}")
        return encrypted_token

def _encrypt_token(plain_token: str) -> str:
    """Encrypts a token and adds 'enc:' prefix."""
    if not plain_token:
        return plain_token
        
    manager = _get_encryption_manager()
    if not manager:
        return plain_token
        
    try:
        blob = manager.encrypt_to_blob(plain_token.encode('utf-8'))
        return f"enc:{base64.b64encode(blob).decode('utf-8')}"
    except Exception as e:
        print(f"[DB] Encryption failed: {e}")
        return plain_token


# ============================================================
# RESILIENT DATA ACCESS FUNCTIONS
# ============================================================

@with_fallback(cache_key_fn=lambda company_id: f"ventas:{company_id}", ttl_hours=1)
def get_ventas(company_id: str) -> pd.DataFrame:
    """
    Fetches sales data with local cache fallback.
    CRITICAL: Sales data is essential, uses short cache TTL.
    """
    supabase = get_supabase()
    if not supabase:
        raise ConnectionError("Supabase not configured")
    
    response = supabase.table("ventas") \
        .select("cliente_id, fecha_venta, monto_total") \
        .eq("company_id", company_id) \
        .execute()
    
    if not response.data:
        return pd.DataFrame()
    
    df = pd.DataFrame(response.data)
    df.columns = ['customer_id', 'order_date', 'revenue']
    return df


@with_fallback(cache_key_fn=lambda company_id: f"gastos:{company_id}", ttl_hours=6)
def get_gastos(company_id: str) -> pd.DataFrame:
    """
    Fetches marketing expenses with cache fallback.
    Less critical than sales, longer cache TTL.
    """
    supabase = get_supabase()
    if not supabase:
        raise ConnectionError("Supabase not configured")
    
    response = supabase.table("gastos_marketing") \
        .select("fecha, canal, inversion, impresiones, clics") \
        .eq("company_id", company_id) \
        .execute()
    
    if not response.data:
        return pd.DataFrame()
    
    return pd.DataFrame(response.data)


@with_fallback(cache_key_fn=lambda company_id: f"tokens:{company_id}", ttl_hours=24)
def get_company_tokens(company_id: str) -> dict:
    """
    Retrieves integration tokens with cache fallback.
    Tokens can be cached longer (change infrequently).
    Decrypts sensitive tokens on-the-fly.
    """
    supabase = get_supabase()
    if not supabase:
        raise ConnectionError("Supabase not configured")
    
    response = supabase.table("integrations") \
        .select("service_name, account_id, access_token, api_key, shop_url, credentials") \
        .eq("company_id", company_id) \
        .execute()
    
    tokens = {item['service_name']: item for item in response.data}
    
    # Decrypt sensitive fields
    for service, data in tokens.items():
        if data.get('access_token'):
            data['access_token'] = _decrypt_token(data['access_token'])
        if data.get('api_key'):
            data['api_key'] = _decrypt_token(data['api_key'])
            
    return tokens


@with_retry_queue(table_name="integrations")
def save_company_token(company_id: str, service_name: str, \
                     access_token: str = None, api_key: str = None, \
                     account_id: str = None, shop_url: str = None, \
                     credentials: dict = None) -> bool:
    """
    Saves or updates an integration record with mandatory encryption.
    """
    supabase = get_supabase()
    if not supabase:
        raise ConnectionError("Supabase not configured")
    
    # Encrypt sensitive fields
    data = {
        "company_id": company_id,
        "service_name": service_name,
        "updated_at": pd.Timestamp.now().isoformat()
    }
    
    if access_token:
        data["access_token"] = _encrypt_token(access_token)
    if api_key:
        data["api_key"] = _encrypt_token(api_key)
    if account_id:
        data["account_id"] = account_id
    if shop_url:
        data["shop_url"] = shop_url
    if credentials:
        data["credentials"] = credentials # credentials are typically non-standard/complex blobs
        
    try:
        supabase.table("integrations") \
            .upsert(data) \
            .execute()
        return True
    except Exception as e:
        print(f"[DB] Failed to save token for {service_name}: {e}")
        return False


@with_fallback(cache_key_fn=lambda company_id: f"metrics:{company_id}", ttl_hours=1)
def get_dashboard_metrics(company_id: str) -> dict:
    """
    Fetches aggregate metrics with cache fallback.
    """
    supabase = get_supabase()
    if not supabase:
        raise ConnectionError("Supabase not configured")
    
    res = supabase.table("insights_jsonb") \
        .select("data") \
        .eq("company_id", company_id) \
        .eq("insight_type", "dashboard_metrics") \
        .order("created_at", desc=True) \
        .limit(1) \
        .execute()
    
    if res.data:
        return res.data[0]['data']
    
    # Fallback to legacy table
    res_legacy = supabase.table("insights_core") \
        .select("ltv_predicho_12m, probabilidad_churn") \
        .eq("company_id", company_id) \
        .execute()
    
    df = pd.DataFrame(res_legacy.data)
    if df.empty:
        return {"ltv_total": 0, "avg_churn": 0, "customer_count": 0}
    
    return {
        "ltv_total": float(df['ltv_predicho_12m'].sum()),
        "avg_churn": float(df['probabilidad_churn'].mean()),
        "customer_count": len(df)
    }


@with_fallback(cache_key_fn=lambda company_id, limit=5: f"vips:{company_id}:{limit}")
def get_high_risk_vips(company_id: str, limit: int = 5) -> list:
    """
    Fetches high-risk VIPs with cache fallback.
    """
    supabase = get_supabase()
    if not supabase:
        raise ConnectionError("Supabase not configured")
    
    res = supabase.table("insights_core") \
        .select("probabilidad_churn, ltv_predicho_12m, clientes(nombre, email)") \
        .eq("company_id", company_id) \
        .order("ltv_predicho_12m", desc=True) \
        .limit(limit) \
        .execute()
    
    return res.data


# ============================================================
# JSONB-STYLE FLEXIBLE WRITES
# ============================================================

@with_retry_queue(table_name="insights_jsonb")
def save_insights_jsonb(company_id: str, insight_type: str, 
                        data: Dict, metadata: Dict = None) -> bool:
    """
    Saves insights to JSONB table with flexible schema.
    NON-CRITICAL: If this fails, it's queued for retry.
    
    Args:
        company_id: Company identifier
        insight_type: Type of insight (ltv_predictions, churn_alerts, mmm_results, etc.)
        data: The actual insight data (any structure)
        metadata: Optional metadata (model_version, confidence, etc.)
    
    Returns:
        True if saved successfully, False if queued for retry
    """
    supabase = get_supabase()
    if not supabase:
        raise ConnectionError("Supabase not configured")
    
    payload = {
        "company_id": company_id,
        "insight_type": insight_type,
        "data": data,
        "metadata": metadata or {},
        "created_at": datetime.now().isoformat()
    }
    
    supabase.table("insights_jsonb").insert(payload).execute()
    
    # Also save to local cache
    cache = get_local_cache()
    cache.save_prediction(
        company_id=company_id,
        prediction_type=insight_type,
        output_data=data,
        confidence=metadata.get("confidence") if metadata else None,
        model_version=metadata.get("model_version") if metadata else None
    )
    
    return True


@with_retry_queue(table_name="predictions_cache")
def save_predictions(company_id: str, predictions: List[Dict], 
                     model_type: str, training_metrics: Dict = None) -> bool:
    """
    Saves LTV/Churn predictions with JSONB flexibility.
    """
    supabase = get_supabase()
    if not supabase:
        raise ConnectionError("Supabase not configured")
    
    payload = {
        "company_id": company_id,
        "insight_type": "customer_predictions",
        "data": {
            "predictions": predictions,
            "model_type": model_type,
            "generated_at": datetime.now().isoformat()
        },
        "metadata": {
            "training_metrics": training_metrics,
            "count": len(predictions)
        }
    }
    
    supabase.table("insights_jsonb").insert(payload).execute()
    return True


@with_retry_queue(table_name="mmm_results")
def save_mmm_results(company_id: str, optimization_results: Dict,
                     channel_posteriors: Dict = None) -> bool:
    """
    Saves MMM optimization results with JSONB flexibility.
    """
    supabase = get_supabase()
    if not supabase:
        raise ConnectionError("Supabase not configured")
    
    payload = {
        "company_id": company_id,
        "insight_type": "mmm_optimization",
        "data": {
            "optimal_allocation": optimization_results.get("optimal_allocation"),
            "expected_revenue": optimization_results.get("expected_revenue"),
            "marginal_roas": optimization_results.get("marginal_roas"),
            "channels": optimization_results.get("channels")
        },
        "metadata": {
            "tuned_parameters": optimization_results.get("tuned_parameters"),
            "posteriors": channel_posteriors,
            "generated_at": datetime.now().isoformat()
        }
    }
    
    supabase.table("insights_jsonb").insert(payload).execute()
    return True


# ============================================================
# RETRY PROCESSOR
# ============================================================

def process_retry_queue():
    """
    Process pending retries. Should be called periodically (e.g., via cron or background task).
    """
    cache = get_local_cache()
    supabase = get_supabase()
    
    if not supabase:
        print("[DB] Supabase unavailable, skipping retry processing")
        return
    
    pending = cache.get_pending_retries()
    print(f"[DB] Processing {len(pending)} pending retries")
    
    for item in pending:
        try:
            # Re-attempt the write
            data = item['data'].get('payload', {})
            
            if isinstance(data, list):
                supabase.table(item['table_name']).upsert(data).execute()
            else:
                supabase.table(item['table_name']).insert(data).execute()
            
            cache.mark_retry_success(item['id'])
            print(f"[DB] Retry success for {item['table_name']}")
            
        except Exception as e:
            cache.mark_retry_failed(item['id'])
            print(f"[DB] Retry failed for {item['table_name']}: {e}")


# ============================================================
# HEALTH CHECK
# ============================================================

def check_database_health() -> Dict:
    """
    Check database connectivity and cache status.
    """
    result = {
        "supabase_available": False,
        "local_cache_available": False,
        "pending_retries": 0,
        "status": "degraded"
    }
    
    # Check Supabase
    try:
        supabase = get_supabase()
        if supabase:
            # Simple query to test connection
            supabase.table("clientes").select("id").limit(1).execute()
            result["supabase_available"] = True
    except Exception as e:
        result["supabase_error"] = str(e)
    
    # Check local cache
    try:
        cache = get_local_cache()
        result["local_cache_available"] = True
        result["pending_retries"] = len(cache.get_pending_retries())
    except Exception as e:
        result["cache_error"] = str(e)
    
    # Determine overall status
    if result["supabase_available"] and result["local_cache_available"]:
        result["status"] = "healthy"
    elif result["local_cache_available"]:
        result["status"] = "degraded_offline_mode"
    else:
        result["status"] = "unhealthy"
    
    return result


# ============================================================
# SQL SCHEMA FOR SUPABASE (JSONB TABLES)
# ============================================================

SUPABASE_SCHEMA_SQL = """
-- Run this in Supabase SQL Editor to create the JSONB tables

-- Flexible insights table with JSONB
CREATE TABLE IF NOT EXISTS insights_jsonb (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID NOT NULL REFERENCES companies(id),
    insight_type TEXT NOT NULL,
    data JSONB NOT NULL,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Indexes for common queries
    CONSTRAINT valid_insight_type CHECK (insight_type IN (
        'customer_predictions', 'mmm_optimization', 'cohort_analysis',
        'dashboard_metrics', 'churn_alerts', 'bundle_recommendations'
    ))
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_insights_company ON insights_jsonb(company_id);
CREATE INDEX IF NOT EXISTS idx_insights_type ON insights_jsonb(insight_type);
CREATE INDEX IF NOT EXISTS idx_insights_created ON insights_jsonb(created_at DESC);

-- GIN index for JSONB queries
CREATE INDEX IF NOT EXISTS idx_insights_data_gin ON insights_jsonb USING GIN (data);

-- Row Level Security
ALTER TABLE insights_jsonb ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can only see their company insights" ON insights_jsonb
    FOR SELECT USING (company_id = auth.uid());

CREATE POLICY "Users can insert their company insights" ON insights_jsonb
    FOR INSERT WITH CHECK (company_id = auth.uid());
"""
