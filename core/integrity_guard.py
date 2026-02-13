"""
Integrity Guard - Tactics Intelligence 2.0
M├│dulo especializado en la detecci├│n de anomal├¡as y auditor├¡a de integridad
sin alteraci├│n de los datos originales.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, field

@dataclass
class IntegrityIssue:
    type: str  # 'duplicate', 'gap', 'critical_nan', 'outlier'
    severity: str  # 'critical', 'warning', 'info'
    column: Optional[str]
    message: str
    affected_rows: int
    sample_ids: List[Any]
    metadata: Dict[str, Any] = field(default_factory=dict)

class IntegrityGuard:
    """
    Guardian de la integridad de los datos.
    Detecta problemas de calidad profunda y genera reportes de auditor├¡a.
    """
    
    def __init__(self):
        self.issues: List[IntegrityIssue] = []

    def scan(self, df: pd.DataFrame, context: str = "generic") -> List[IntegrityIssue]:
        """
        Escanea un DataFrame en busca de anomal├¡as.
        """
        self.issues = []
        
        if df is None or df.empty:
            return self.issues

        # 1. Detecci├│n de Duplicados Exactos y L├│gicos
        self._detect_duplicates(df, context)
        
        # 2. Detecci├│n de NaNs en Columnas Cr├¡ticas
        self._detect_critical_nans(df, context)
        
        # 3. An├ílisis de Gaps Temporales (si aplica)
        self._analyze_temporal_gaps(df, context)
        
        return self.issues

    def _detect_duplicates(self, df: pd.DataFrame, context: str):
        """Detecta duplicados basados en claves l├│gicas"""
        # Duplicados exactos (toda la fila)
        exact_dupes = df.duplicated().sum()
        if exact_dupes > 0:
            self.issues.append(IntegrityIssue(
                type="duplicate",
                severity="warning",
                column=None,
                message=f"Se detectaron {exact_dupes} filas exactamente duplicadas.",
                affected_rows=int(exact_dupes),
                sample_ids=[],
                metadata={"scope": "exact_row"}
            ))

        # Duplicados l├│gicos por contexto
        if context == "ventas":
            key_cols = ['order_id']
            if all(col in df.columns for col in key_cols):
                logical_dupes = df.duplicated(subset=key_cols).sum()
                if logical_dupes > 0:
                    sample = df[df.duplicated(subset=key_cols)]['order_id'].head(5).tolist()
                    self.issues.append(IntegrityIssue(
                        type="duplicate",
                        severity="critical",
                        column="order_id",
                        message=f"Conflicto de integridad: {logical_dupes} registros comparten el mismo ID de pedido.",
                        affected_rows=int(logical_dupes),
                        sample_ids=sample,
                        metadata={"scope": "logical_key"}
                    ))
        
        elif context == "gastos":
            key_cols = ['fecha', 'canal', 'campaign_name']
            cols_present = [c for c in key_cols if c in df.columns]
            if len(cols_present) >= 2:
                logical_dupes = df.duplicated(subset=cols_present).sum()
                if logical_dupes > 0:
                    self.issues.append(IntegrityIssue(
                        type="duplicate",
                        severity="warning",
                        column=None,
                        message=f"Posible duplicidad de gasto: {logical_dupes} registros coinciden en fecha y canal.",
                        affected_rows=int(logical_dupes),
                        sample_ids=[],
                        metadata={"scope": "marketing_overlap"}
                    ))

    def _detect_critical_nans(self, df: pd.DataFrame, context: str):
        """Busca NaNs en columnas vitales para el negocio"""
        critical_cols = {
            "ventas": ["revenue", "customer_id", "order_date"],
            "gastos": ["inversion", "fecha", "canal"],
            "clientes": ["customer_id"]
        }.get(context, [])

        for col in critical_cols:
            if col in df.columns:
                nans = df[col].isna().sum()
                if nans > 0:
                    self.issues.append(IntegrityIssue(
                        type="critical_nan",
                        severity="critical",
                        column=col,
                        message=f"Faltan datos financieros cr├¡ticos: {nans} valores nulos en '{col}'.",
                        affected_rows=int(nans),
                        sample_ids=[],
                        metadata={}
                    ))

    def _analyze_temporal_gaps(self, df: pd.DataFrame, context: str):
        """Identifica silencios en la data (gaps)"""
        date_col = None
        for col in ['fecha', 'order_date', 'date', 'created_at']:
            if col in df.columns:
                date_col = col
                break
        
        if not date_col:
            return

        try:
            dates = pd.to_datetime(df[date_col], errors='coerce').dropna().sort_values()
            if len(dates) < 10:
                return

            # Calcular diferencias entre registros consecutivos
            diffs = dates.diff().dt.days
            
            # Si hay gaps > 7 d├¡as en un flujo que deber├¡a ser diario
            large_gaps = diffs[diffs > 7]
            if not large_gaps.empty:
                gap_count = len(large_gaps)
                max_gap = int(large_gaps.max())
                self.issues.append(IntegrityIssue(
                    type="gap",
                    severity="warning",
                    column=date_col,
                    message=f"Detectados {gap_count} 'huecos' temporales de m├ís de una semana. El mayor es de {max_gap} d├¡as.",
                    affected_rows=gap_count,
                    sample_ids=[],
                    metadata={"max_gap_days": max_gap}
                ))
        except Exception:
            pass
