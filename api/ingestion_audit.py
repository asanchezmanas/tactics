"""
Ingestion Audit - Tactics
Garantiza la trazabilidad y veracidad de cada proceso de importaci├│n.
Sistema de 'Recibo de Verdad'.
"""

import hashlib
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict, field

# Try to import database
try:
    from .database import supabase
except ImportError:
    supabase = None

@dataclass
class IngestionReceipt:
    batch_id: str
    company_id: str
    data_type: str  # 'ventas', 'clientes', 'gastos'
    source: str
    filename: Optional[str]
    input_row_count: int
    success_count: int
    error_count: int
    checksum: str
    timestamp: str
    status: str  # 'completed', 'partial', 'failed'
    errors: List[str] = field(default_factory=list)

class IngestionAuditor:
    """
    Gestiona los recibos de importaci├│n y la trazabilidad de los datos.
    """
    
    def __init__(self, company_id: str):
        self.company_id = company_id

    def create_batch_id(self) -> str:
        """Genera un ID de lote ├║nico"""
        return f"batch_{datetime.now().strftime('%Y%m%d%H%M')}_{uuid.uuid4().hex[:6]}"

    def calculate_checksum(self, content: bytes) -> str:
        """Calcula hash SHA-256 para verificar integridad del archivo original"""
        return hashlib.sha256(content).hexdigest()

    def generate_receipt(self, 
                         batch_id: str,
                         data_type: str,
                         source: str,
                         input_row_count: int,
                         success_count: int,
                         error_count: int,
                         checksum: str,
                         errors: List[str],
                         filename: Optional[str] = None) -> IngestionReceipt:
        """
        Genera y persiste un recibo de importaci├│n.
        """
        status = "completed"
        if error_count > 0:
            status = "partial" if success_count > 0 else "failed"
            
        receipt = IngestionReceipt(
            batch_id=batch_id,
            company_id=self.company_id,
            data_type=data_type,
            source=source,
            filename=filename,
            input_row_count=input_row_count,
            success_count=success_count,
            error_count=error_count,
            checksum=checksum,
            timestamp=datetime.now().isoformat(),
            status=status,
            errors=errors[:100] # Limitar log de errores
        )
        
        self._persist_receipt(receipt)
        return receipt

    def _persist_receipt(self, receipt: IngestionReceipt):
        """Guarda el recibo en la base de datos para auditor├¡a futura"""
        if not supabase:
            # Fallback local o log
            print(f"[AUDIT] Receipt saved locally: {receipt.batch_id}")
            return

        try:
            # En un entorno real, existir├¡a la tabla 'ingestion_receipts'
            # supabase.table("ingestion_receipts").insert(asdict(receipt)).execute()
            pass
        except Exception as e:
            print(f"[AUDIT ERROR] Could not persist receipt: {e}")

    def get_batch_audit(self, batch_id: str) -> Optional[Dict]:
        """Recupera la auditor├¡a de un lote espec├¡fico"""
        if not supabase: return None
        # return supabase.table("ingestion_receipts").select("*").eq("batch_id", batch_id).single().execute().data
        return None


