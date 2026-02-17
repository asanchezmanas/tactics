"""
Data Quality Analyzer - Tactics
Analizador gen├®rico de calidad de datos para determinar el nivel de algoritmos disponibles.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional, List, Dict, Any
import pandas as pd
import numpy as np
from core.integrity_guard import IntegrityGuard, IntegrityIssue


class DataQualityLevel(Enum):
    """Niveles de calidad de datos"""
    CRITICAL = "critical"     # Datos insuficientes
    LOW = "low"               # Datos m├¡nimos  
    MEDIUM = "medium"         # Datos aceptables
    HIGH = "high"             # Datos buenos
    EXCELLENT = "excellent"   # Datos ├│ptimos


@dataclass
class DataQualityReport:
    """Reporte completo de calidad de datos"""
    # M├®tricas b├ísicas
    row_count: int
    column_count: int
    
    # Rango temporal
    date_column: Optional[str]
    date_min: Optional[datetime]
    date_max: Optional[datetime]
    date_span_days: int
    date_span_months: int
    
    # Completitud
    completeness_score: float  # 0-100
    missing_by_column: Dict[str, float]
    
    # Densidad
    density_score: float  # 0-100
    records_per_month: float
    
    # Recencia
    days_since_last_record: int
    is_stale: bool  # >90 d├¡as sin datos
    
    # Puntuaci├│n general
    overall_score: int  # 0-100
    quality_level: DataQualityLevel
    
    # Recomendaciones
    recommendations: List[str] = field(default_factory=list)
    
    # Algoritmos
    unlocked_algorithm_count: int = 0
    locked_algorithm_count: int = 0
    
    # Hallazgos de Integridad Profunda
    integrity_issues: List[IntegrityIssue] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el reporte a diccionario para API"""
        return {
            "row_count": self.row_count,
            "column_count": self.column_count,
            "date_range": {
                "column": self.date_column,
                "min": self.date_min.isoformat() if self.date_min else None,
                "max": self.date_max.isoformat() if self.date_max else None,
                "span_days": self.date_span_days,
                "span_months": self.date_span_months,
            },
            "completeness": {
                "score": round(self.completeness_score, 1),
                "missing_by_column": self.missing_by_column,
            },
            "density": {
                "score": round(self.density_score, 1),
                "records_per_month": round(self.records_per_month, 1),
            },
            "recency": {
                "days_since_last": self.days_since_last_record,
                "is_stale": self.is_stale,
            },
            "overall": {
                "score": self.overall_score,
                "level": self.quality_level.value,
            },
            "algorithms": {
                "unlocked": self.unlocked_algorithm_count,
                "locked": self.locked_algorithm_count,
            },
            "integrity": {
                "issue_count": len(self.integrity_issues),
                "critical_count": len([i for i in self.integrity_issues if i.severity == "critical"]),
                "issues": [
                    {"type": i.type, "message": i.message, "severity": i.severity} 
                    for i in self.integrity_issues
                ]
            },
            "recommendations": self.recommendations,
        }


class DataQualityAnalyzer:
    """
    Analizador gen├®rico de calidad de datos.
    
    Funciona con cualquier DataFrame de pandas y detecta autom├íticamente:
    - Columnas de fecha
    - Columnas de ID (cliente, usuario, etc.)
    - Columnas num├®ricas (valores, importes)
    
    Uso:
        analyzer = DataQualityAnalyzer()
        report = analyzer.analyze(df)
        print(report.overall_score)  # 0-100
    """
    
    # Patrones para detectar columnas de fecha
    DATE_PATTERNS = [
        'date', 'order_date', 'timestamp', 'fecha', 'created', 'updated', 
        'purchase_date', 'transaction_date',
        'created_at', 'updated_at', 'time', 'dt'
    ]
    
    # Patrones para detectar columnas de ID
    ID_PATTERNS = [
        'id', 'customer_id', 'user_id', 'client_id', 'uid',
        'cliente_id', 'usuario_id', 'account_id'
    ]
    
    # Patrones para detectar columnas de valor/importe
    VALUE_PATTERNS = [
        'spend', 'revenue', 'amount', 'value', 'total', 'price', 'sales',
        'importe', 'valor', 'precio', 'monto', 'cost'
    ]
    
    # Umbrales de calidad
    MIN_RECORDS = 50
    MIN_MONTHS_BASIC = 1
    MIN_MONTHS_STANDARD = 3
    MIN_MONTHS_ADVANCED = 12
    MIN_MONTHS_PRECISION = 24
    MIN_COMPLETENESS = 70
    STALE_THRESHOLD_DAYS = 90
    
    def __init__(self):
        self._date_column: Optional[str] = None
        self._id_column: Optional[str] = None
        self._value_column: Optional[str] = None
        self.guard = IntegrityGuard()
    
    def analyze(self, df: pd.DataFrame) -> DataQualityReport:
        """
        Analiza un DataFrame y retorna un reporte de calidad.
        
        Args:
            df: DataFrame con los datos a analizar
            
        Returns:
            DataQualityReport con todas las m├®tricas
        """
        if df is None or df.empty:
            return self._empty_report()
        
        # Detectar columnas clave
        self._detect_columns(df)
        
        # Calcular m├®tricas
        row_count = len(df)
        column_count = len(df.columns)
        
        # Rango temporal
        date_min, date_max, span_days, span_months = self._analyze_dates(df)
        
        # Completitud
        completeness, missing_by_column = self._analyze_completeness(df)
        
        # Densidad
        density, records_per_month = self._analyze_density(df, span_months)
        
        # Recencia
        days_since_last = self._calculate_recency(date_max)
        is_stale = days_since_last > self.STALE_THRESHOLD_DAYS
        
        # Puntuaci├│n general
        overall_score = self._calculate_overall_score(
            row_count, span_months, completeness, density, is_stale
        )
        quality_level = self._score_to_level(overall_score)
        
        # Auditor├¡a de Integridad Profunda
        integrity_issues = self.guard.scan(df, context="general")
        
        # Recomendaciones
        recommendations = self._generate_recommendations(
            row_count, span_months, completeness, density, is_stale, integrity_issues
        )
        
        # Contar algoritmos (se actualizar├í por AlgorithmTierService)
        from core.algorithm_tiers import AlgorithmTierService
        tier_service = AlgorithmTierService()
        unlocked, locked = tier_service.count_algorithms_by_data(span_months, row_count)
        
        return DataQualityReport(
            row_count=row_count,
            column_count=column_count,
            date_column=self._date_column,
            date_min=date_min,
            date_max=date_max,
            date_span_days=span_days,
            date_span_months=span_months,
            completeness_score=completeness,
            missing_by_column=missing_by_column,
            density_score=density,
            records_per_month=records_per_month,
            days_since_last_record=days_since_last,
            is_stale=is_stale,
            overall_score=overall_score,
            quality_level=quality_level,
            recommendations=recommendations,
            unlocked_algorithm_count=unlocked,
            locked_algorithm_count=locked,
            integrity_issues=integrity_issues
        )
    
    def _detect_columns(self, df: pd.DataFrame) -> None:
        """Detecta autom├íticamente columnas clave"""
        columns_lower = {col.lower(): col for col in df.columns}
        
        # Detectar columna de fecha
        for pattern in self.DATE_PATTERNS:
            for col_lower, col_original in columns_lower.items():
                if pattern in col_lower:
                    # Verificar que sea parseable como fecha
                    try:
                        pd.to_datetime(df[col_original].dropna().head(10))
                        self._date_column = col_original
                        break
                    except:
                        continue
            if self._date_column:
                break
        
        # Detectar columna de ID
        for pattern in self.ID_PATTERNS:
            for col_lower, col_original in columns_lower.items():
                if pattern in col_lower:
                    self._id_column = col_original
                    break
            if self._id_column:
                break
        
        # Detectar columna de valor
        for pattern in self.VALUE_PATTERNS:
            for col_lower, col_original in columns_lower.items():
                if pattern in col_lower:
                    self._value_column = col_original
                    break
            if self._value_column:
                break
    
    def _analyze_dates(self, df: pd.DataFrame) -> tuple:
        """Analiza el rango temporal de los datos"""
        if not self._date_column or self._date_column not in df.columns:
            return None, None, 0, 0
        
        try:
            dates = pd.to_datetime(df[self._date_column], errors='coerce')
            dates = dates.dropna()
            
            if dates.empty:
                return None, None, 0, 0
            
            date_min = dates.min().to_pydatetime()
            date_max = dates.max().to_pydatetime()
            span_days = (date_max - date_min).days
            span_months = max(1, span_days // 30)
            
            return date_min, date_max, span_days, span_months
        except Exception:
            return None, None, 0, 0
    
    def _analyze_completeness(self, df: pd.DataFrame) -> tuple:
        """Analiza la completitud de los datos"""
        total_cells = df.size
        null_cells = df.isnull().sum().sum()
        
        completeness = ((total_cells - null_cells) / total_cells) * 100 if total_cells > 0 else 0
        
        # Porcentaje de nulls por columna
        missing_by_column = {}
        for col in df.columns:
            null_pct = (df[col].isnull().sum() / len(df)) * 100
            if null_pct > 0:
                missing_by_column[col] = round(null_pct, 1)
        
        return completeness, missing_by_column
    
    def _analyze_density(self, df: pd.DataFrame, span_months: int) -> tuple:
        """Analiza la densidad de registros"""
        if span_months == 0:
            return 0, 0
        
        records_per_month = len(df) / span_months
        
        # Densidad normalizada (10 records/month = 50%, 100 records/month = 100%)
        density = min(100, (records_per_month / 100) * 100)
        
        return density, records_per_month
    
    def _calculate_recency(self, date_max: Optional[datetime]) -> int:
        """Calcula d├¡as desde el ├║ltimo registro"""
        if not date_max:
            return 999  # Sin fecha = muy antiguo
        
        return (datetime.now() - date_max).days
    
    def _calculate_overall_score(
        self, 
        row_count: int, 
        span_months: int, 
        completeness: float, 
        density: float,
        is_stale: bool
    ) -> int:
        """Calcula puntuaci├│n general 0-100"""
        score = 0
        
        # Volumen (25 puntos)
        if row_count >= 1000:
            score += 25
        elif row_count >= 500:
            score += 20
        elif row_count >= 100:
            score += 15
        elif row_count >= 50:
            score += 10
        else:
            score += 5
        
        # Profundidad temporal (30 puntos)
        if span_months >= 24:
            score += 30
        elif span_months >= 12:
            score += 25
        elif span_months >= 6:
            score += 20
        elif span_months >= 3:
            score += 15
        elif span_months >= 1:
            score += 10
        else:
            score += 5
        
        # Completitud (25 puntos)
        score += int((completeness / 100) * 25)
        
        # Densidad (15 puntos)
        score += int((density / 100) * 15)
        
        # Penalizaci├│n por datos obsoletos (5 puntos)
        if not is_stale:
            score += 5
        
        return min(100, score)
    
    def _score_to_level(self, score: int) -> DataQualityLevel:
        """Convierte puntuaci├│n a nivel de calidad"""
        if score >= 85:
            return DataQualityLevel.EXCELLENT
        elif score >= 70:
            return DataQualityLevel.HIGH
        elif score >= 50:
            return DataQualityLevel.MEDIUM
        elif score >= 30:
            return DataQualityLevel.LOW
        else:
            return DataQualityLevel.CRITICAL
    
    def _generate_recommendations(
        self,
        row_count: int,
        span_months: int,
        completeness: float,
        density: float,
        is_stale: bool,
        integrity_issues: List[IntegrityIssue] = None
    ) -> List[str]:
        """Genera recomendaciones accionables"""
        recs = []
        
        # Deep Integrity Recommendations
        if integrity_issues:
            criticals = [i for i in integrity_issues if i.severity == "critical"]
            if criticals:
                recs.append(f"­ƒÜ¿ CR├ìTICO: Detectados {len(criticals)} problemas de integridad que invalidan la precisi├│n. Revisa la Auditor├¡a.")
            
            gaps = [i for i in integrity_issues if i.type == "gap"]
            if gaps:
                recs.append("Detectados 'silencios' de datos. Las proyecciones en zonas de sombra tendr├ín mayor incertidumbre.")
        
        if row_count < self.MIN_RECORDS:
            recs.append(f"Necesitas al menos {self.MIN_RECORDS} registros para an├ílisis b├ísico. Tienes {row_count}.")
        
        if span_months < self.MIN_MONTHS_STANDARD:
            months_needed = self.MIN_MONTHS_STANDARD - span_months
            recs.append(f"Con {months_needed} meses m├ís de datos, desbloquear├ís LTV y Churn avanzado.")
        
        if span_months < self.MIN_MONTHS_ADVANCED:
            months_needed = self.MIN_MONTHS_ADVANCED - span_months
            recs.append(f"Con {months_needed} meses m├ís, desbloquear├ís MMM con estacionalidad.")
        
        if span_months < self.MIN_MONTHS_PRECISION:
            months_needed = self.MIN_MONTHS_PRECISION - span_months
            recs.append(f"Con {months_needed} meses m├ís, desbloquear├ís predicci├│n LSTM de precisi├│n.")
        
        if completeness < self.MIN_COMPLETENESS:
            recs.append(f"Tu completitud es {completeness:.0f}%. Completa campos vac├¡os para mejorar precisi├│n.")
        
        if is_stale:
            recs.append("Tus datos tienen m├ís de 90 d├¡as de antig├╝edad. Sincroniza para an├ílisis en tiempo real.")
        
        if not recs:
            recs.append("┬íExcelente! Tus datos tienen calidad ├│ptima para todos los algoritmos.")
        
        return recs
    
    def _empty_report(self) -> DataQualityReport:
        """Retorna un reporte vac├¡o para datos insuficientes"""
        return DataQualityReport(
            row_count=0,
            column_count=0,
            date_column=None,
            date_min=None,
            date_max=None,
            date_span_days=0,
            date_span_months=0,
            completeness_score=0,
            missing_by_column={},
            density_score=0,
            records_per_month=0,
            days_since_last_record=999,
            is_stale=True,
            overall_score=0,
            quality_level=DataQualityLevel.CRITICAL,
            recommendations=["No hay datos para analizar. Conecta una fuente de datos."],
            unlocked_algorithm_count=0,
            locked_algorithm_count=0,
        )


# Funci├│n de conveniencia
def analyze_dataframe(df: pd.DataFrame) -> DataQualityReport:
    """Funci├│n helper para an├ílisis r├ípido"""
    return DataQualityAnalyzer().analyze(df)
