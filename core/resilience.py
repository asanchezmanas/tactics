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
import pandas as pd
from dotenv import load_dotenv
from core.secure_vault import EncryptionManager

load_dotenv()

# ============================================================
# CONFIGURATION
# ============================================================

LOCAL_CACHE_PATH = Path(os.getenv("LOCAL_CACHE_PATH", ".cache/tactics.db"))
MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 60

class SecurityError(Exception):
    """Exception raised for security-related failures."""
    pass

# ============================================================
# ENCRYPTION HELPERS
# ============================================================

def _get_encryption_manager() -> Optional[EncryptionManager]:
    """Helper to get EncryptionManager from master key."""
    master_key = os.getenv("VAULT_MASTER_KEY")
    if not master_key:
        return None
    try:
        return EncryptionManager(master_key)
    except Exception as e:
        print(f"[Resilience] Encryption init failed: {e}")
        return None

def decrypt_token(encrypted_token: str) -> str:
    """Decrypts a token if it's encrypted, otherwise returns as is."""
    if not encrypted_token or not encrypted_token.startswith("enc:"):
        return encrypted_token
    
    manager = _get_encryption_manager()
    if not manager:
        return encrypted_token
        
    try:
        blob = base64.b64decode(encrypted_token[4:])
        decrypted = manager.decrypt_from_blob(blob)
        return decrypted.decode('utf-8')
    except Exception as e:
        print(f"[Resilience] Decryption failed: {e}")
        return encrypted_token

def encrypt_token(plain_token: str) -> str:
    """Encrypts a token and adds 'enc:' prefix. Raises SecurityError on failure."""
    if not plain_token:
        return plain_token
        
    manager = _get_encryption_manager()
    if not manager:
        return plain_token
        
    try:
        blob = manager.encrypt_to_blob(plain_token.encode('utf-8'))
        return f"enc:{base64.b64encode(blob).decode('utf-8')}"
    except Exception as e:
        print(f"[Resilience] Encryption failed: {e}")
        # ROBUST: Never return plain text if encryption was requested
        raise SecurityError(f"Encryption failed, blocking to prevent plaintext leak: {e}")

# ============================================================
# LOCAL CACHE (SQLITE)
# ============================================================

class LocalCache:
    """SQLite-based local cache for offline operation and retry queuing."""
    def __init__(self, db_path: Path = LOCAL_CACHE_PATH):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS cache (
                    cache_key TEXT PRIMARY KEY,
                    data JSON NOT NULL,
                    table_name TEXT NOT NULL,
                    company_id TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    expires_at TEXT
                );
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
                CREATE INDEX IF NOT EXISTS idx_cache_company ON cache(company_id);
                CREATE INDEX IF NOT EXISTS idx_retry_next ON retry_queue(next_retry_at);
            """)

    def get(self, cache_key: str) -> Optional[Dict]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT data, expires_at FROM cache WHERE cache_key = ?", (cache_key,))
            row = cursor.fetchone()
            if row:
                data, expires_at = row
                if expires_at and datetime.fromisoformat(expires_at) < datetime.now():
                    self.delete(cache_key)
                    return None
                return json.loads(data)
        return None
    
    def set(self, cache_key: str, data: Any, table_name: str, company_id: str = None, ttl_hours: int = 24):
        expires_at = (datetime.now() + timedelta(hours=ttl_hours)).isoformat()
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("INSERT OR REPLACE INTO cache (cache_key, data, table_name, company_id, expires_at) VALUES (?, ?, ?, ?, ?)",
                        (cache_key, json.dumps(data), table_name, company_id, expires_at))
    
    def delete(self, cache_key: str):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM cache WHERE cache_key = ?", (cache_key,))

    def add_to_retry_queue(self, operation: str, table_name: str, data: Dict, error_message: str):
        next_retry = (datetime.now() + timedelta(seconds=RETRY_DELAY_SECONDS)).isoformat()
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("INSERT INTO retry_queue (operation, table_name, data, error_message, next_retry_at) VALUES (?, ?, ?, ?, ?)",
                        (operation, table_name, json.dumps(data), error_message, next_retry))

    def get_pending_retries(self) -> List[Dict]:
        now = datetime.now().isoformat()
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM retry_queue WHERE next_retry_at <= ?", (now,))
            return [dict(row) for row in cursor.fetchall()]

    def save_prediction(self, company_id: str, prediction_type: str, output_data: Any, input_data: Any = None, confidence: Dict = None, model_version: str = None):
        input_hash = hashlib.md5(json.dumps(input_data, sort_keys=True).encode()).hexdigest() if input_data else "none"
        prediction_id = f"{company_id}:{prediction_type}:{input_hash}"
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO predictions_cache 
                (id, company_id, prediction_type, input_hash, output_data, confidence, model_version)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (prediction_id, company_id, prediction_type, input_hash if input_hash != "none" else None, json.dumps(output_data), json.dumps(confidence), model_version))

    def get_prediction(self, company_id: str, prediction_type: str, input_data: Any = None) -> Optional[Dict]:
        input_hash = hashlib.md5(json.dumps(input_data, sort_keys=True).encode()).hexdigest() if input_data else "none"
        prediction_id = f"{company_id}:{prediction_type}:{input_hash}"
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT output_data, confidence, model_version FROM predictions_cache WHERE id = ?", (prediction_id,))
            row = cursor.fetchone()
            if row:
                return {"output": json.loads(row[0]), "confidence": json.loads(row[1]) if row[1] else None, "model_version": row[2]}
        return None

_local_cache: Optional[LocalCache] = None
def get_local_cache() -> LocalCache:
    global _local_cache
    if _local_cache is None: _local_cache = LocalCache()
    return _local_cache

# ============================================================
# DECORATORS
# ============================================================

def with_fallback(cache_key_fn=None, ttl_hours: int = 24):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache = get_local_cache()
            cache_key = cache_key_fn(*args, **kwargs) if cache_key_fn else None
            try:
                result = func(*args, **kwargs)
                if cache_key and result is not None:
                    data = result.to_dict('records') if isinstance(result, pd.DataFrame) else result
                    cache.set(cache_key, data, func.__name__, ttl_hours=ttl_hours)
                return result
            except Exception as e:
                print(f"[Resilience] Fallback in {func.__name__}: {e}")
                if cache_key:
                    cached = cache.get(cache_key)
                    if cached: return pd.DataFrame(cached) if "DataFrame" in str(func.__annotations__.get('return')) else cached
                return_type = func.__annotations__.get('return')
                if return_type == pd.DataFrame: return pd.DataFrame()
                if return_type == list: return []
                if return_type == dict: return {}
                return None
        return wrapper
    return decorator

def with_retry_queue(table_name: str):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                print(f"[Resilience] Queueing failed write to {table_name}: {e}")
                cache = get_local_cache()
                cache.add_to_retry_queue(
                    operation=func.__name__,
                    table_name=table_name,
                    data=kwargs.get('data', args[1] if len(args) > 1 else {}),
                    error_message=str(e)
                )
                return False
        return wrapper
    return decorator

# --- Circuit Breakers (Mocks) ---
def retry_with_backoff(max_retries=3, initial_delay=1.0):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper
    return decorator

def shopify_breaker(func): return func
meta_breaker = shopify_breaker
google_breaker = shopify_breaker
klaviyo_breaker = shopify_breaker
stripe_breaker = shopify_breaker
ga4_breaker = shopify_breaker
gsc_breaker = shopify_breaker
class DataGuard:
    """Static utility for data validation and quality gating."""
    
    @staticmethod
    def validate_sales_data(df: pd.DataFrame) -> List[str]:
        errors = []
        if df.empty:
            errors.append("Empty sales data")
            return errors
        
        required = ['customer_id', 'order_date', 'revenue']
        for col in required:
            if col not in df.columns:
                errors.append(f"Missing required column: {col}")
        
        # Check for extreme values or corrupt data
        if not errors:
            if (df['revenue'] < 0).any():
                errors.append("Negative revenue detected")
        
        return errors

    @staticmethod
    def validate_marketing_data(df: pd.DataFrame) -> List[str]:
        errors = []
        if df.empty: return [] # Marketing data is optional
        
        required = ['date', 'channel', 'spend']
        for col in required:
            if col not in df.columns:
                errors.append(f"Missing required column: {col}")
        
        return errors
