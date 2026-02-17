"""
Diagnostic Engine: Intelligence 2.0 Sandbox
Processes external CSV data with fuzzy mapping to feed the Live Sandbox UI.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional
from core.metrics_factory import BusinessMetricsFactory

class DiagnosticEngine:
    """Engine to digest unformatted client data into Tactics Intelligence 2.0 format."""

    COLUMN_MAPPING = {
        'customer_id': ['cliente_id', 'id_cliente', 'usuario_id', 'customer', 'customer_id', 'email', 'uid'],
        'order_date': ['fecha', 'date', 'order_date', 'fecha_venta', 'timestamp', 'created_at'],
        'revenue': ['monto', 'valor', 'revenue', 'total', 'precio', 'price', 'amount', 'sales'],
        'channel': ['canal', 'channel', 'source', 'medio', 'origin', 'acquisition_channel'],
        'product_id': ['producto_id', 'product_id', 'sku', 'item_id', 'ref']
    }

    def __init__(self, company_id: str = "demo_diagnostic"):
        self.company_id = company_id
        self.factory = BusinessMetricsFactory(company_id)

    def process_csv(self, file_path_or_buffer: Any) -> Dict[str, Any]:
        """Reads CSV, maps columns, and calculates insights."""
        try:
            # 1. Automated Detection (Delimiter & Encoding)
            import io
            import csv
            
            content_sample = ""
            if isinstance(file_path_or_buffer, (str, bytes)):
                content_sample = file_path_or_buffer[:4096]
            elif hasattr(file_path_or_buffer, 'read'):
                content_sample = file_path_or_buffer.read(4096)
                file_path_or_buffer.seek(0)
            
            try:
                if isinstance(content_sample, bytes):
                    content_sample = content_sample.decode('utf-8', errors='ignore')
                dialect = csv.Sniffer().sniff(content_sample, delimiters=[',', ';', '\t', '|'])
                sep = dialect.delimiter
            except:
                sep = ',' # Fallback

            df = pd.read_csv(file_path_or_buffer, sep=sep)
            
            if df.empty:
                return {"success": False, "error": "CSV is empty"}

            # 2. Fuzzy Mapping & Header Cleaning
            df.columns = [str(c).strip().lower() for c in df.columns]
            mapped_df = self._map_columns(df)
            
            # Validation
            # Match SQL schema and DataIngetion requirements
            required = ['id', 'customer_id', 'order_date', 'revenue']
            missing = [r for r in required if r not in mapped_df.columns]
            if not 'id' in mapped_df.columns and 'order_id' in df.columns: # legacy handling
                 mapped_df['id'] = df['order_id']
                 missing = [r for r in required if r not in mapped_df.columns]
            
            if missing:
                return {"success": False, "error": f"Missing required columns (fuzzy match failed): {missing}"}

            # 2. Data Cleaning
            mapped_df['order_date'] = pd.to_datetime(mapped_df['order_date'], errors='coerce')
            mapped_df['revenue'] = pd.to_numeric(mapped_df['revenue'], errors='coerce')
            mapped_df = mapped_df.dropna(subset=['id', 'customer_id', 'order_date', 'revenue'])

            if len(mapped_df) < 20:
                return {"success": False, "error": "Insufficient data for quality analysis (min 20 valid rows)"}

            # 3. Calculate Intelligence 2.0 Metrics
            # For the demo, we mock empty marketing data if not provided to avoid audit errors
            mock_mkt = pd.DataFrame(columns=['date', 'channel', 'spend'])
            
            report = self.factory.calculate_all(mapped_df, mock_mkt)
            
            return {
                "success": True,
                "metrics": {
                    "growth": report.growth,
                    "pareto": report.deep_synthesis.get('pareto_concentration', {}),
                    "basket_affinity": report.deep_synthesis.get('basket_affinity', []),
                    "retention": report.retention.get('weighted_retention_rate', 0),
                    "aov": report.unit_economics.get('aov', 0),
                    "sample_size": len(mapped_df),
                    "signals": report.signals_for_ai
                }
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _map_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Attempts to rename columns to standard format based on common patterns."""
        new_cols = {}
        for target, aliases in self.COLUMN_MAPPING.items():
            for col in df.columns:
                if col.lower().strip() in aliases:
                    new_cols[col] = target
                    break
        
        return df.rename(columns=new_cols)

if __name__ == "__main__":
    # Test with dummy data
    engine = DiagnosticEngine()
    dummy_csv = "cliente_id,fecha,valor\n1,2023-01-01,100\n1,2023-02-01,150\n2,2023-01-15,200"
    from io import StringIO
    result = engine.process_csv(StringIO(dummy_csv))
    print(result)
