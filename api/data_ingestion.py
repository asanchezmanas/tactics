"""
Universal Data Ingestion Layer

Provides flexible data import from ANY source:
- CSV upload with auto-column detection
- Webhook/API endpoint for push integrations
- Template-based mapping for known sources (Shopify, Square, Holded, etc.)
- Manual data entry support
- Automatic encrypted backup to SecureVault (Internxt)

All data normalizes to 4 core tables:
- clientes (customers)
- ventas (sales/orders)
- productos (products with COGS)
- gastos_marketing (marketing spend)
"""
import csv
import json
import io
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path

# Try to import database, fallback gracefully
try:
    from .database import supabase
except ImportError:
    supabase = None

# Try to import SecureVault for encrypted backups
try:
    from core.secure_vault import SecureVault, backup_csv_to_vault
    VAULT_AVAILABLE = True
except ImportError:
    VAULT_AVAILABLE = False


# ============================================================
# NORMALIZED SCHEMAS
# ============================================================

SCHEMA_CLIENTES = {
    "required": ["customer_id"],
    "optional": ["email", "nombre", "telefono", "created_at", "metadata"],
    "types": {
        "customer_id": str,
        "email": str,
        "nombre": str,
        "created_at": "datetime"
    }
}

SCHEMA_VENTAS = {
    "required": ["order_id", "customer_id", "order_date", "revenue"],
    "optional": ["canal_origen", "productos", "descuento", "moneda"],
    "types": {
        "order_id": str,
        "customer_id": str,
        "order_date": "datetime",
        "revenue": float
    }
}

SCHEMA_PRODUCTOS = {
    "required": ["product_id", "name", "price"],
    "optional": ["cogs", "shipping", "storage_cost", "sku", "category"],
    "types": {
        "product_id": str,
        "name": str,
        "price": float,
        "cogs": float
    }
}

SCHEMA_GASTOS = {
    "required": ["fecha", "canal", "inversion"],
    "optional": ["impresiones", "clics", "conversiones", "campaign_name"],
    "types": {
        "fecha": "date",
        "canal": str,
        "inversion": float
    }
}


# ============================================================
# SOURCE TEMPLATES (Mapeo de columnas por fuente)
# ============================================================

SOURCE_TEMPLATES = {
    # ECOMMERCE
    "shopify": {
        "ventas": {
            "Name": "order_id",
            "Email": "customer_id",
            "Created at": "order_date",
            "Total": "revenue",
            "Source name": "canal_origen"
        },
        "date_format": "%Y-%m-%d %H:%M:%S"
    },
    "woocommerce": {
        "ventas": {
            "Order ID": "order_id",
            "Customer Email": "customer_id",
            "Order Date": "order_date",
            "Order Total": "revenue"
        },
        "date_format": "%Y-%m-%d"
    },
    
    # TPVs
    "square": {
        "ventas": {
            "Transaction ID": "order_id",
            "Customer ID": "customer_id",
            "Date": "order_date",
            "Total Collected": "revenue",
            "Source": "canal_origen"
        },
        "date_format": "%Y-%m-%dT%H:%M:%S"
    },
    "sumup": {
        "ventas": {
            "Transaction code": "order_id",
            "Card holder name": "customer_id",
            "Date": "order_date",
            "Amount": "revenue"
        },
        "date_format": "%d/%m/%Y %H:%M"
    },
    "clover": {
        "ventas": {
            "Order ID": "order_id",
            "Customer": "customer_id",
            "Created Time": "order_date",
            "Total": "revenue"
        },
        "date_format": "%m/%d/%Y %I:%M %p"
    },
    "izettle": {
        "ventas": {
            "Receipt number": "order_id",
            "Seller": "customer_id",
            "Date": "order_date",
            "Total": "revenue"
        },
        "date_format": "%Y-%m-%d"
    },
    
    # ERPs
    "holded": {
        "ventas": {
            "Número": "order_id",
            "Contacto": "customer_id",
            "Fecha": "order_date",
            "Total": "revenue"
        },
        "clientes": {
            "ID": "customer_id",
            "Email": "email",
            "Nombre": "nombre"
        },
        "date_format": "%d/%m/%Y"
    },
    "factorial": {
        "clientes": {
            "id": "customer_id",
            "email": "email",
            "full_name": "nombre"
        }
    },
    
    # MARKETING
    "meta_ads": {
        "gastos": {
            "Date": "fecha",
            "Campaign name": "campaign_name",
            "Amount spent": "inversion",
            "Impressions": "impresiones",
            "Link clicks": "clics",
            "Results": "conversiones"
        },
        "default_canal": "facebook",
        "date_format": "%Y-%m-%d"
    },
    "google_ads": {
        "gastos": {
            "Day": "fecha",
            "Campaign": "campaign_name",
            "Cost": "inversion",
            "Impressions": "impresiones",
            "Clicks": "clics",
            "Conversions": "conversiones"
        },
        "default_canal": "google",
        "date_format": "%Y-%m-%d"
    },
    "tiktok_ads": {
        "gastos": {
            "Date": "fecha",
            "Campaign name": "campaign_name",
            "Cost": "inversion",
            "Impression": "impresiones",
            "Click": "clics",
            "Conversion": "conversiones"
        },
        "default_canal": "tiktok",
        "date_format": "%Y-%m-%d"
    },
    
    # GENERIC (auto-detect)
    "generic": {
        "ventas": {
            "order_id": "order_id",
            "customer_id": "customer_id",
            "date": "order_date",
            "amount": "revenue",
            "total": "revenue",
            "revenue": "revenue"
        }
    }
}


# ============================================================
# DATA INGESTION CLASS
# ============================================================

class DataIngestion:
    """
    Universal data ingestion handler.
    
    Supports:
    - CSV files with auto-mapping
    - JSON payloads via webhook
    - Direct dict insertion
    """
    
    def __init__(self, company_id: str):
        self.company_id = company_id
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.stats = {"inserted": 0, "updated": 0, "skipped": 0, "errors": 0}
    
    # ─────────────────────────────────────────────────────────
    # CSV INGESTION
    # ─────────────────────────────────────────────────────────
    
    def ingest_csv(self, csv_content: str, data_type: str, 
                   source: str = "generic",
                   backup_to_vault: bool = True) -> Dict[str, Any]:
        """
        Ingest CSV data.
        
        Args:
            csv_content: Raw CSV string
            data_type: 'ventas', 'clientes', 'productos', 'gastos'
            source: Source template to use (e.g., 'shopify', 'square', 'generic')
            backup_to_vault: If True, backup raw CSV to SecureVault before processing
            
        Returns:
            Dict with stats, vault_id (if backed up), and any errors
        """
        vault_info = None
        
        # Backup to vault BEFORE processing (Zero-Knowledge backup)
        if backup_to_vault and VAULT_AVAILABLE:
            try:
                filename = f"{data_type}_{source}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                vault_info = backup_csv_to_vault(
                    self.company_id, 
                    filename, 
                    csv_content.encode()
                )
            except Exception as e:
                self.warnings.append(f"Vault backup failed: {e}")
        
        try:
            reader = csv.DictReader(io.StringIO(csv_content))
            rows = list(reader)
        except Exception as e:
            return {"success": False, "error": f"CSV parse error: {e}"}
        
        if not rows:
            return {"success": False, "error": "CSV is empty"}
        
        # Get column mapping for this source
        template = SOURCE_TEMPLATES.get(source, SOURCE_TEMPLATES["generic"])
        mapping = template.get(data_type, {})
        date_format = template.get("date_format", "%Y-%m-%d")
        
        # Auto-detect columns if no mapping found
        if not mapping:
            mapping = self._auto_detect_columns(rows[0].keys(), data_type)
        
        # Transform and insert
        normalized_rows = []
        for i, row in enumerate(rows):
            try:
                normalized = self._map_row(row, mapping, data_type, date_format)
                if normalized:
                    normalized["company_id"] = self.company_id
                    normalized_rows.append(normalized)
            except Exception as e:
                self.errors.append(f"Row {i+1}: {e}")
                self.stats["errors"] += 1
        
        # Insert to database
        if normalized_rows:
            self._batch_insert(data_type, normalized_rows)
        
        result = {
            "success": True,
            "stats": self.stats,
            "errors": self.errors[:10],  # First 10 errors
            "warnings": self.warnings[:10],
            "sample": normalized_rows[:3] if normalized_rows else []
        }
        
        # Add vault info if backup was successful
        if vault_info:
            result["vault_backup"] = {
                "vault_id": vault_info.get("vault_id"),
                "encrypted": vault_info.get("encrypted", False),
                "timestamp": vault_info.get("timestamp")
            }
        
        return result
    
    def preview_csv(self, csv_content: str, data_type: str,
                    source: str = "generic") -> Dict[str, Any]:
        """
        Preview CSV mapping without inserting.
        
        Returns detected columns and sample transformed data.
        """
        try:
            reader = csv.DictReader(io.StringIO(csv_content))
            rows = list(reader)[:5]  # First 5 rows only
        except Exception as e:
            return {"success": False, "error": f"CSV parse error: {e}"}
        
        if not rows:
            return {"success": False, "error": "CSV is empty"}
        
        # Get or detect mapping
        template = SOURCE_TEMPLATES.get(source, SOURCE_TEMPLATES["generic"])
        mapping = template.get(data_type, {})
        
        if not mapping:
            mapping = self._auto_detect_columns(rows[0].keys(), data_type)
        
        # Show what would be mapped
        original_columns = list(rows[0].keys())
        mapped_columns = {orig: mapping.get(orig, "❌ unmapped") for orig in original_columns}
        
        # Sample transformation
        sample_transformed = []
        for row in rows[:3]:
            try:
                transformed = self._map_row(row, mapping, data_type)
                sample_transformed.append(transformed)
            except Exception as e:
                sample_transformed.append({"error": str(e)})
        
        return {
            "success": True,
            "original_columns": original_columns,
            "column_mapping": mapped_columns,
            "available_sources": list(SOURCE_TEMPLATES.keys()),
            "sample_original": rows[:3],
            "sample_transformed": sample_transformed,
            "total_rows": len(rows)
        }
    
    # ─────────────────────────────────────────────────────────
    # JSON/WEBHOOK INGESTION
    # ─────────────────────────────────────────────────────────
    
    def ingest_json(self, data: List[Dict], data_type: str) -> Dict[str, Any]:
        """
        Ingest JSON data (from webhook or API).
        
        Data should already be in normalized format.
        """
        if not data:
            return {"success": False, "error": "No data provided"}
        
        # Validate and insert
        normalized_rows = []
        for i, row in enumerate(data):
            try:
                validated = self._validate_row(row, data_type)
                validated["company_id"] = self.company_id
                normalized_rows.append(validated)
            except Exception as e:
                self.errors.append(f"Row {i+1}: {e}")
                self.stats["errors"] += 1
        
        if normalized_rows:
            self._batch_insert(data_type, normalized_rows)
        
        return {
            "success": True,
            "stats": self.stats,
            "errors": self.errors[:10]
        }
    
    # ─────────────────────────────────────────────────────────
    # SINGLE ROW INSERTION (for manual entry)
    # ─────────────────────────────────────────────────────────
    
    def insert_venta(self, order_id: str, customer_id: str, 
                     order_date: str, revenue: float,
                     canal: str = "manual", **kwargs) -> Dict:
        """Insert a single sale manually."""
        row = {
            "company_id": self.company_id,
            "order_id": order_id,
            "customer_id": customer_id,
            "order_date": order_date,
            "revenue": revenue,
            "canal_origen": canal,
            **kwargs
        }
        return self._insert_single("ventas", row)
    
    def insert_cliente(self, customer_id: str, email: str = None,
                       nombre: str = None, **kwargs) -> Dict:
        """Insert a single customer manually."""
        row = {
            "company_id": self.company_id,
            "customer_id": customer_id,
            "email": email,
            "nombre": nombre,
            **kwargs
        }
        return self._insert_single("clientes", row)
    
    def insert_producto(self, product_id: str, name: str, price: float,
                        cogs: float = None, **kwargs) -> Dict:
        """Insert a single product manually."""
        row = {
            "company_id": self.company_id,
            "product_id": product_id,
            "name": name,
            "price": price,
            "cogs": cogs,
            **kwargs
        }
        return self._insert_single("productos", row)
    
    def insert_gasto(self, fecha: str, canal: str, inversion: float,
                     **kwargs) -> Dict:
        """Insert marketing spend manually."""
        row = {
            "company_id": self.company_id,
            "fecha": fecha,
            "canal": canal,
            "inversion": inversion,
            **kwargs
        }
        return self._insert_single("gastos_marketing", row)
    
    # ─────────────────────────────────────────────────────────
    # INTERNAL HELPERS
    # ─────────────────────────────────────────────────────────
    
    def _auto_detect_columns(self, columns: List[str], data_type: str) -> Dict[str, str]:
        """Auto-detect column mapping based on common names."""
        mapping = {}
        
        # Common column name variations
        COMMON_MAPPINGS = {
            "ventas": {
                "order_id": ["order_id", "order id", "id", "transaction_id", "invoice", "numero"],
                "customer_id": ["customer_id", "customer", "client", "email", "cliente"],
                "order_date": ["date", "order_date", "created_at", "fecha", "timestamp"],
                "revenue": ["total", "amount", "revenue", "price", "monto", "importe"]
            },
            "clientes": {
                "customer_id": ["id", "customer_id", "client_id"],
                "email": ["email", "correo", "mail"],
                "nombre": ["name", "nombre", "full_name", "customer_name"]
            },
            "productos": {
                "product_id": ["id", "product_id", "sku", "codigo"],
                "name": ["name", "title", "nombre", "product"],
                "price": ["price", "precio", "amount"],
                "cogs": ["cost", "cogs", "coste", "costo"]
            },
            "gastos": {
                "fecha": ["date", "fecha", "day"],
                "canal": ["channel", "canal", "source", "platform"],
                "inversion": ["spend", "cost", "amount", "inversion", "gasto"]
            }
        }
        
        type_mappings = COMMON_MAPPINGS.get(data_type, {})
        columns_lower = {c.lower().strip(): c for c in columns}
        
        for target_field, variations in type_mappings.items():
            for var in variations:
                if var in columns_lower:
                    mapping[columns_lower[var]] = target_field
                    break
        
        return mapping
    
    def _map_row(self, row: Dict, mapping: Dict[str, str], 
                 data_type: str, date_format: str = "%Y-%m-%d") -> Dict:
        """Map a row using the provided column mapping."""
        result = {}
        
        for orig_col, target_col in mapping.items():
            if orig_col in row:
                value = row[orig_col]
                
                # Type conversion
                if target_col in ["order_date", "fecha", "created_at"]:
                    try:
                        if isinstance(value, str):
                            # Try multiple date formats
                            for fmt in [date_format, "%Y-%m-%d", "%d/%m/%Y", "%Y-%m-%dT%H:%M:%S"]:
                                try:
                                    value = datetime.strptime(value, fmt).isoformat()
                                    break
                                except ValueError:
                                    continue
                    except Exception:
                        pass
                
                elif target_col in ["revenue", "price", "cogs", "inversion"]:
                    try:
                        # Remove currency symbols and parse
                        value = str(value).replace("€", "").replace("$", "").replace(",", ".").strip()
                        value = float(value) if value else 0.0
                    except ValueError:
                        value = 0.0
                
                result[target_col] = value
        
        return result
    
    def _validate_row(self, row: Dict, data_type: str) -> Dict:
        """Validate a row against schema."""
        schema = {
            "ventas": SCHEMA_VENTAS,
            "clientes": SCHEMA_CLIENTES,
            "productos": SCHEMA_PRODUCTOS,
            "gastos": SCHEMA_GASTOS
        }.get(data_type)
        
        if not schema:
            raise ValueError(f"Unknown data type: {data_type}")
        
        # Check required fields
        for field in schema["required"]:
            if field not in row or row[field] is None:
                raise ValueError(f"Missing required field: {field}")
        
        return row
    
    def _batch_insert(self, data_type: str, rows: List[Dict]):
        """Batch insert rows to database."""
        if not supabase:
            # Local fallback - just count
            self.stats["inserted"] = len(rows)
            return
        
        table_map = {
            "ventas": "ventas",
            "clientes": "clientes",
            "productos": "products",
            "gastos": "gastos_marketing"
        }
        
        table = table_map.get(data_type)
        if not table:
            return
        
        try:
            result = supabase.table(table).upsert(rows).execute()
            self.stats["inserted"] = len(rows)
        except Exception as e:
            self.errors.append(f"Database error: {e}")
            self.stats["errors"] += len(rows)
    
    def _insert_single(self, table: str, row: Dict) -> Dict:
        """Insert a single row."""
        if not supabase:
            return {"success": True, "id": "local-" + str(hash(str(row)))}
        
        try:
            result = supabase.table(table).insert(row).execute()
            return {"success": True, "data": result.data}
        except Exception as e:
            return {"success": False, "error": str(e)}


# ============================================================
# CONVENIENCE FUNCTIONS
# ============================================================

def get_available_sources() -> List[Dict[str, str]]:
    """Get list of supported data sources with descriptions."""
    sources = [
        {"id": "shopify", "name": "Shopify", "category": "Ecommerce"},
        {"id": "woocommerce", "name": "WooCommerce", "category": "Ecommerce"},
        {"id": "square", "name": "Square", "category": "TPV"},
        {"id": "sumup", "name": "SumUp", "category": "TPV"},
        {"id": "clover", "name": "Clover", "category": "TPV"},
        {"id": "izettle", "name": "iZettle/Zettle", "category": "TPV"},
        {"id": "holded", "name": "Holded", "category": "ERP"},
        {"id": "factorial", "name": "Factorial", "category": "ERP"},
        {"id": "meta_ads", "name": "Meta Ads", "category": "Marketing"},
        {"id": "google_ads", "name": "Google Ads", "category": "Marketing"},
        {"id": "tiktok_ads", "name": "TikTok Ads", "category": "Marketing"},
        {"id": "generic", "name": "Generic/Custom", "category": "Other"}
    ]
    return sources


def get_template_columns(source: str, data_type: str) -> Dict[str, str]:
    """Get expected column names for a source template."""
    template = SOURCE_TEMPLATES.get(source, {})
    return template.get(data_type, {})
