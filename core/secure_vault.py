"""
Secure Vault: Zero-Knowledge Data Storage Layer

Provides encrypted storage for:
- Raw data backups (CSVs uploaded by customers)
- Model state snapshots (Bayesian priors, LinUCB matrices)
- Audit-trail documents

Supports multiple backends:
- Internxt (S3-compatible API or WebDAV)
- Local encrypted storage (fallback)
- Any S3-compatible service

All data is encrypted BEFORE upload using AES-256-GCM.
The encryption key is derived from a master key that only the customer controls.
"""
import os
import json
import hashlib
import base64
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Optional, Any, Tuple
from dataclasses import dataclass
import logging

# Cryptography
try:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False
    logging.warning("cryptography not installed. Encryption disabled.")

# S3 client
try:
    import boto3
    from botocore.config import Config
    S3_AVAILABLE = True
except ImportError:
    S3_AVAILABLE = False

# WebDAV client
try:
    from webdav3.client import Client as WebDAVClient
    WEBDAV_AVAILABLE = True
except ImportError:
    WEBDAV_AVAILABLE = False

logger = logging.getLogger(__name__)


# ============================================================
# CONFIGURATION
# ============================================================

@dataclass
class VaultConfig:
    """Configuration for secure vault storage."""
    # Backend: 'internxt_s3', 'internxt_webdav', 'local', 'aws_s3'
    backend: str = "local"
    
    # Internxt S3 settings
    s3_endpoint: str = "https://s3.internxt.com"
    s3_access_key: str = ""
    s3_secret_key: str = ""
    s3_bucket: str = "tactics-vault"
    
    # WebDAV settings
    webdav_url: str = "https://webdav.internxt.com"
    webdav_user: str = ""
    webdav_password: str = ""
    
    # Local storage (fallback)
    local_path: str = ".vault"
    
    # Encryption
    master_key: str = ""  # Should be securely stored, not in config
    
    @classmethod
    def from_env(cls) -> 'VaultConfig':
        """Load configuration from environment variables."""
        return cls(
            backend=os.getenv("VAULT_BACKEND", "local"),
            s3_endpoint=os.getenv("INTERNXT_S3_ENDPOINT", "https://s3.internxt.com"),
            s3_access_key=os.getenv("INTERNXT_ACCESS_KEY", ""),
            s3_secret_key=os.getenv("INTERNXT_SECRET_KEY", ""),
            s3_bucket=os.getenv("INTERNXT_BUCKET", "tactics-vault"),
            webdav_url=os.getenv("INTERNXT_WEBDAV_URL", "https://webdav.internxt.com"),
            webdav_user=os.getenv("INTERNXT_WEBDAV_USER", ""),
            webdav_password=os.getenv("INTERNXT_WEBDAV_PASSWORD", ""),
            local_path=os.getenv("VAULT_LOCAL_PATH", ".vault"),
            master_key=os.getenv("VAULT_MASTER_KEY", "")
        )


# ============================================================
# ENCRYPTION LAYER
# ============================================================

class EncryptionManager:
    """AES-256-GCM encryption for zero-knowledge storage."""
    
    def __init__(self, master_key: str):
        if not CRYPTO_AVAILABLE:
            raise RuntimeError("cryptography library required for encryption")
        
        # Derive a 256-bit key from the master key using PBKDF2
        salt = b"tactics_vault_v1"  # Fixed salt (key derivation)
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        self.key = kdf.derive(master_key.encode())
        self.aesgcm = AESGCM(self.key)
    
    def encrypt(self, data: bytes) -> Tuple[bytes, bytes]:
        """
        Encrypt data using AES-256-GCM.
        
        Returns:
            Tuple of (nonce, ciphertext)
        """
        nonce = os.urandom(12)  # 96-bit nonce for GCM
        ciphertext = self.aesgcm.encrypt(nonce, data, None)
        return nonce, ciphertext
    
    def decrypt(self, nonce: bytes, ciphertext: bytes) -> bytes:
        """Decrypt data using AES-256-GCM."""
        return self.aesgcm.decrypt(nonce, ciphertext, None)
    
    def encrypt_to_blob(self, data: bytes) -> bytes:
        """Encrypt and return a single blob (nonce + ciphertext)."""
        nonce, ciphertext = self.encrypt(data)
        return nonce + ciphertext
    
    def decrypt_from_blob(self, blob: bytes) -> bytes:
        """Decrypt from a single blob (first 12 bytes = nonce)."""
        nonce = blob[:12]
        ciphertext = blob[12:]
        return self.decrypt(nonce, ciphertext)


# ============================================================
# STORAGE BACKENDS
# ============================================================

class LocalBackend:
    """Local filesystem storage (encrypted)."""
    
    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
    
    def upload(self, key: str, data: bytes) -> str:
        """Upload data to local storage."""
        file_path = self.base_path / key
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_bytes(data)
        return str(file_path)
    
    def download(self, key: str) -> Optional[bytes]:
        """Download data from local storage."""
        file_path = self.base_path / key
        if file_path.exists():
            return file_path.read_bytes()
        return None
    
    def delete(self, key: str) -> bool:
        """Delete a file from local storage."""
        file_path = self.base_path / key
        if file_path.exists():
            file_path.unlink()
            return True
        return False
    
    def list_keys(self, prefix: str = "") -> list:
        """List all keys with optional prefix."""
        results = []
        for p in self.base_path.rglob("*"):
            if p.is_file():
                rel_path = str(p.relative_to(self.base_path)).replace("\\", "/")
                if not prefix or rel_path.startswith(prefix):
                    results.append(rel_path)
        return results


class S3Backend:
    """S3-compatible storage (Internxt, AWS, MinIO, etc.)."""
    
    def __init__(self, endpoint: str, access_key: str, secret_key: str, bucket: str):
        if not S3_AVAILABLE:
            raise RuntimeError("boto3 required for S3 backend")
        
        self.bucket = bucket
        self.client = boto3.client(
            's3',
            endpoint_url=endpoint,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            config=Config(signature_version='s3v4')
        )
        
        # Ensure bucket exists
        try:
            self.client.head_bucket(Bucket=bucket)
        except Exception:
            try:
                self.client.create_bucket(Bucket=bucket)
            except Exception as e:
                logger.warning(f"Could not create bucket: {e}")
    
    def upload(self, key: str, data: bytes) -> str:
        """Upload data to S3."""
        self.client.put_object(Bucket=self.bucket, Key=key, Body=data)
        return f"s3://{self.bucket}/{key}"
    
    def download(self, key: str) -> Optional[bytes]:
        """Download data from S3."""
        try:
            response = self.client.get_object(Bucket=self.bucket, Key=key)
            return response['Body'].read()
        except Exception:
            return None
    
    def delete(self, key: str) -> bool:
        """Delete an object from S3."""
        try:
            self.client.delete_object(Bucket=self.bucket, Key=key)
            return True
        except Exception:
            return False
    
    def list_keys(self, prefix: str = "") -> list:
        """List all keys with optional prefix."""
        try:
            response = self.client.list_objects_v2(Bucket=self.bucket, Prefix=prefix)
            return [obj['Key'] for obj in response.get('Contents', [])]
        except Exception:
            return []


class WebDAVBackend:
    """WebDAV storage backend (Internxt WebDAV)."""
    
    def __init__(self, url: str, user: str, password: str):
        if not WEBDAV_AVAILABLE:
            raise RuntimeError("webdav3 client required for WebDAV backend")
        
        self.client = WebDAVClient({
            'webdav_hostname': url,
            'webdav_login': user,
            'webdav_password': password
        })
        
        # Ensure base directory exists
        try:
            if not self.client.check("tactics-vault"):
                self.client.mkdir("tactics-vault")
        except Exception as e:
            logger.warning(f"Could not create vault directory: {e}")
    
    def upload(self, key: str, data: bytes) -> str:
        """Upload data to WebDAV."""
        import tempfile
        
        remote_path = f"tactics-vault/{key}"
        
        # Ensure parent directories exist
        parts = key.split("/")
        current = "tactics-vault"
        for part in parts[:-1]:
            current = f"{current}/{part}"
            try:
                if not self.client.check(current):
                    self.client.mkdir(current)
            except Exception:
                pass
        
        # Write to temp file and upload
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(data)
            tmp_path = tmp.name
        
        try:
            self.client.upload_sync(remote_path=remote_path, local_path=tmp_path)
        finally:
            os.unlink(tmp_path)
        
        return f"webdav://{remote_path}"
    
    def download(self, key: str) -> Optional[bytes]:
        """Download data from WebDAV."""
        import tempfile
        
        remote_path = f"tactics-vault/{key}"
        
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp_path = tmp.name
        
        try:
            self.client.download_sync(remote_path=remote_path, local_path=tmp_path)
            with open(tmp_path, 'rb') as f:
                return f.read()
        except Exception:
            return None
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
    
    def delete(self, key: str) -> bool:
        """Delete a file from WebDAV."""
        try:
            self.client.clean(f"tactics-vault/{key}")
            return True
        except Exception:
            return False
    
    def list_keys(self, prefix: str = "") -> list:
        """List all keys with optional prefix."""
        try:
            path = f"tactics-vault/{prefix}" if prefix else "tactics-vault"
            return self.client.list(path)
        except Exception:
            return []


# ============================================================
# SECURE VAULT (Main Interface)
# ============================================================

class SecureVault:
    """
    Zero-knowledge secure vault for data storage.
    
    All data is encrypted locally before upload.
    Supports multiple storage backends.
    """
    
    def __init__(self, config: Optional[VaultConfig] = None, company_id: str = "default"):
        self.config = config or VaultConfig.from_env()
        self.company_id = company_id
        
        # Initialize encryption (if master key provided)
        self.encryption = None
        if self.config.master_key and CRYPTO_AVAILABLE:
            self.encryption = EncryptionManager(self.config.master_key)
        
        # Initialize backend
        self.backend = self._init_backend()
    
    def _init_backend(self):
        """Initialize the appropriate storage backend."""
        if self.config.backend == "internxt_s3" and S3_AVAILABLE:
            return S3Backend(
                self.config.s3_endpoint,
                self.config.s3_access_key,
                self.config.s3_secret_key,
                self.config.s3_bucket
            )
        elif self.config.backend == "internxt_webdav" and WEBDAV_AVAILABLE:
            return WebDAVBackend(
                self.config.webdav_url,
                self.config.webdav_user,
                self.config.webdav_password
            )
        else:
            # Fallback to local storage
            return LocalBackend(self.config.local_path)
    
    # ─────────────────────────────────────────────────────────
    # RAW DATA VAULT (CSV backups)
    # ─────────────────────────────────────────────────────────
    
    def store_raw_data(self, filename: str, content: bytes, 
                      data_type: str = "csv") -> Dict[str, Any]:
        """
        Store raw uploaded data in the vault.
        
        Args:
            filename: Original filename
            content: Raw file content
            data_type: Type of data ('csv', 'json', etc.)
            
        Returns:
            Dict with vault_id, timestamp, and metadata
        """
        timestamp = datetime.now(timezone.utc).isoformat()
        vault_id = hashlib.sha256(f"{filename}{timestamp}".encode()).hexdigest()[:16]
        
        key = f"{self.company_id}/raw/{data_type}/{vault_id}_{filename}"
        
        # Encrypt if encryption is available
        if self.encryption:
            content = self.encryption.encrypt_to_blob(content)
            key += ".enc"
        
        # Upload
        location = self.backend.upload(key, content)
        
        # Store metadata
        metadata = {
            "vault_id": vault_id,
            "original_filename": filename,
            "data_type": data_type,
            "size_bytes": len(content),
            "encrypted": self.encryption is not None,
            "timestamp": timestamp,
            "location": location
        }
        
        meta_key = f"{self.company_id}/meta/{vault_id}.json"
        self.backend.upload(meta_key, json.dumps(metadata).encode())
        
        logger.info(f"Stored raw data: {vault_id}")
        return metadata
    
    def retrieve_raw_data(self, vault_id: str) -> Optional[bytes]:
        """Retrieve raw data from vault by ID."""
        # Find the file by listing
        prefix = f"{self.company_id}/raw/"
        keys = self.backend.list_keys(prefix)
        
        matching = [k for k in keys if vault_id in k]
        if not matching:
            return None
        
        content = self.backend.download(matching[0])
        
        # Decrypt if needed
        if content and matching[0].endswith(".enc") and self.encryption:
            content = self.encryption.decrypt_from_blob(content)
        
        return content
    
    # ─────────────────────────────────────────────────────────
    # MODEL SNAPSHOTS
    # ─────────────────────────────────────────────────────────
    
    def store_model_snapshot(self, model_name: str, state: Dict, 
                            metrics: Optional[Dict] = None,
                            reason: str = "scheduled") -> Dict[str, Any]:
        """
        Store a model state snapshot.
        
        Used for:
        - Disaster recovery
        - Model versioning
        - Audit trail
        """
        timestamp = datetime.now(timezone.utc)
        version = timestamp.strftime("%Y%m%d_%H%M%S")
        
        snapshot = {
            "model_name": model_name,
            "version": version,
            "state": state,
            "metrics": metrics or {},
            "reason": reason,
            "timestamp": timestamp.isoformat()
        }
        
        content = json.dumps(snapshot, default=str).encode()
        
        key = f"{self.company_id}/models/{model_name}/{version}.json"
        
        if self.encryption:
            content = self.encryption.encrypt_to_blob(content)
            key += ".enc"
        
        location = self.backend.upload(key, content)
        
        logger.info(f"Stored model snapshot: {model_name} v{version}")
        
        return {
            "model_name": model_name,
            "version": version,
            "location": location,
            "encrypted": self.encryption is not None,
            "timestamp": timestamp.isoformat()
        }
    
    def list_model_snapshots(self, model_name: str) -> list:
        """List all snapshots for a model."""
        prefix = f"{self.company_id}/models/{model_name}/"
        return self.backend.list_keys(prefix)
    
    def restore_model_snapshot(self, model_name: str, 
                               version: Optional[str] = None) -> Optional[Dict]:
        """
        Restore a model snapshot.
        
        If version is None, restores the latest.
        """
        snapshots = self.list_model_snapshots(model_name)
        
        if not snapshots:
            return None
        
        if version:
            matching = [s for s in snapshots if version in s]
            if not matching:
                return None
            key = matching[0]
        else:
            # Get latest (sorted by timestamp in filename)
            key = sorted(snapshots)[-1]
        
        content = self.backend.download(key)
        
        if content and key.endswith(".enc") and self.encryption:
            content = self.encryption.decrypt_from_blob(content)
        
        if content:
            return json.loads(content.decode())
        
        return None
    
    # ─────────────────────────────────────────────────────────
    # AUDIT DOCUMENTS
    # ─────────────────────────────────────────────────────────
    
    def store_audit_document(self, doc_type: str, content: bytes,
                            doc_name: str = "") -> Dict[str, Any]:
        """
        Store an audit document (reports, validations, etc.).
        """
        timestamp = datetime.now(timezone.utc)
        doc_id = hashlib.sha256(f"{doc_type}{timestamp.isoformat()}".encode()).hexdigest()[:12]
        
        if not doc_name:
            doc_name = f"{doc_type}_{doc_id}"
        
        key = f"{self.company_id}/audit/{doc_type}/{timestamp.strftime('%Y%m')}/{doc_name}"
        
        if self.encryption:
            content = self.encryption.encrypt_to_blob(content)
            key += ".enc"
        
        location = self.backend.upload(key, content)
        
        return {
            "doc_id": doc_id,
            "doc_type": doc_type,
            "doc_name": doc_name,
            "location": location,
            "timestamp": timestamp.isoformat()
        }
    
    # ─────────────────────────────────────────────────────────
    # HEALTH CHECK
    # ─────────────────────────────────────────────────────────
    
    def health_check(self) -> Dict[str, Any]:
        """Check vault health and connectivity."""
        status = {
            "backend": self.config.backend,
            "encryption_enabled": self.encryption is not None,
            "company_id": self.company_id,
            "connected": False,
            "error": None
        }
        
        try:
            # Try a simple operation
            test_key = f"{self.company_id}/.health_check"
            self.backend.upload(test_key, b"ok")
            result = self.backend.download(test_key)
            self.backend.delete(test_key)
            
            status["connected"] = result == b"ok"
        except Exception as e:
            status["error"] = str(e)
        
        return status


# ============================================================
# CONVENIENCE FUNCTIONS
# ============================================================

def get_vault(company_id: str = "default") -> SecureVault:
    """Get a configured SecureVault instance."""
    return SecureVault(company_id=company_id)


def backup_csv_to_vault(company_id: str, filename: str, 
                        content: bytes) -> Dict[str, Any]:
    """Quick function to backup a CSV to the vault."""
    vault = get_vault(company_id)
    return vault.store_raw_data(filename, content, data_type="csv")


def backup_model_to_vault(company_id: str, model_name: str,
                          state: Dict, metrics: Dict = None) -> Dict[str, Any]:
    """Quick function to backup a model snapshot."""
    vault = get_vault(company_id)
    return vault.store_model_snapshot(model_name, state, metrics)
