"""
Algorithm Tiers - Tactics
Sistema de desbloqueo progresivo de algoritmos seg├║n calidad de datos.
"""

from dataclasses import dataclass
from enum import Enum
from typing import List, Dict, Any, Tuple, Optional


class AlgorithmTier(Enum):
    """Niveles de algoritmos seg├║n requisitos de datos y suscripci├│n"""
    INTELLIGENCE = "intelligence"   # LTV, Segmentaci├│n básica
    OPTIMISATION = "optimisation"   # MMM SLSQP, Canales, Basket
    PRECISION = "precision"      # Bayesian MMM, LSTM, LTV-Weighted ROAS


@dataclass
class AlgorithmSpec:
    """Especificaci├│n de un algoritmo"""
    id: str
    name: str
    description: str
    tier: AlgorithmTier
    min_months: int
    min_records: int
    category: str  # 'ltv', 'churn', 'mmm', 'segmentation', 'forecast'
    icon: str = "­ƒôè"
    
    def is_unlocked(self, months: int, records: int) -> bool:
        """Verifica si el algoritmo est├í desbloqueado"""
        return months >= self.min_months and records >= self.min_records
    
    def months_to_unlock(self, current_months: int) -> int:
        """Meses adicionales necesarios para desbloquear"""
        return max(0, self.min_months - current_months)
    
    def records_to_unlock(self, current_records: int) -> int:
        """Registros adicionales necesarios para desbloquear"""
        return max(0, self.min_records - current_records)
    
    def to_dict(self, months: int = 0, records: int = 0) -> Dict[str, Any]:
        """Convierte a diccionario para API"""
        unlocked = self.is_unlocked(months, records)
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "tier": self.tier.value,
            "category": self.category,
            "icon": self.icon,
            "requirements": {
                "min_months": self.min_months,
                "min_records": self.min_records,
            },
            "status": {
                "unlocked": unlocked,
                "months_needed": self.months_to_unlock(months) if not unlocked else 0,
                "records_needed": self.records_to_unlock(records) if not unlocked else 0,
            }
        }


# Cat├ílogo de todos los algoritmos disponibles
ALGORITHM_CATALOG: List[AlgorithmSpec] = [
    # === TIER INTELLIGENCE ===
    AlgorithmSpec(
        id="rfm_basic",
        name="Segmentaci├│n RFM",
        description="Clasifica clientes por Recencia, Frecuencia y Valor Monetario",
        tier=AlgorithmTier.INTELLIGENCE,
        min_months=1,
        min_records=50,
        category="segmentation",
        icon="­ƒæÑ"
    ),
    AlgorithmSpec(
        id="cohort_basic",
        name="Cohortes B├ísicas",
        description="Agrupa clientes por fecha de primera compra",
        tier=AlgorithmTier.INTELLIGENCE,
        min_months=2,
        min_records=100,
        category="segmentation",
        icon="­ƒôà"
    ),
    AlgorithmSpec(
        id="revenue_summary",
        name="Resumen de Ingresos",
        description="M├®tricas agregadas de facturaci├│n y tendencia",
        tier=AlgorithmTier.INTELLIGENCE,
        min_months=1,
        min_records=30,
        category="ltv",
        icon="­ƒÆÁ"
    ),
    
    # === TIER OPTIMISATION ===
    AlgorithmSpec(
        id="ltv_bgnbd",
        name="LTV Probabil├¡stico (BG/NBD)",
        description="Proyecci├│n de valor de vida del cliente con modelo Buy-Till-You-Die",
        tier=AlgorithmTier.OPTIMISATION,
        min_months=3,
        min_records=100,
        category="ltv",
        icon="­ƒÆÄ"
    ),
    AlgorithmSpec(
        id="churn_probability",
        name="Probabilidad de Churn",
        description="Detecta clientes en riesgo de abandono",
        tier=AlgorithmTier.OPTIMISATION,
        min_months=6,
        min_records=200,
        category="churn",
        icon="ÔÜá´©Å"
    ),
    AlgorithmSpec(
        id="clv_simple",
        name="CLV Hist├│rico",
        description="Valor de cliente basado en historial real",
        tier=AlgorithmTier.OPTIMISATION,
        min_months=3,
        min_records=100,
        category="ltv",
        icon="­ƒôê"
    ),
    AlgorithmSpec(
        id="retention_curve",
        name="Curva de Retenci├│n",
        description="An├ílisis de supervivencia de clientes por cohorte",
        tier=AlgorithmTier.OPTIMISATION,
        min_months=6,
        min_records=200,
        category="churn",
        icon="­ƒôë"
    ),
    
    # === TIER OPTIMISATION (Continued) ===
    AlgorithmSpec(
        id="mmm_hill",
        name="MMM con Curvas Hill",
        description="Modelado de Mix de Medios con saturaci├│n y adstock",
        tier=AlgorithmTier.OPTIMISATION,
        min_months=12,
        min_records=52,  # semanal
        category="mmm",
        icon="­ƒôè"
    ),
    AlgorithmSpec(
        id="seasonality",
        name="An├ílisis de Estacionalidad",
        description="Detecta patrones estacionales en ventas y marketing",
        tier=AlgorithmTier.OPTIMISATION,
        min_months=12,
        min_records=365,
        category="forecast",
        icon="­ƒîè"
    ),
    AlgorithmSpec(
        id="channel_attribution",
        name="Atribuci├│n Multi-Canal",
        description="Asigna cr├®dito a canales con modelo probabil├¡stico",
        tier=AlgorithmTier.OPTIMISATION,
        min_months=6,
        min_records=500,
        category="mmm",
        icon="­ƒöÇ"
    ),
    AlgorithmSpec(
        id="budget_optimizer",
        name="Optimizador de Presupuesto",
        description="Rebalanceo ├│ptimo de inversi├│n entre canales",
        tier=AlgorithmTier.OPTIMISATION,
        min_months=12,
        min_records=52,
        category="mmm",
        icon="ÔÜí"
    ),
    
    # === TIER PRECISION ===
    AlgorithmSpec(
        id="lstm_forecast",
        name="Predicci├│n LSTM",
        description="Pron├│stico de ventas con redes neuronales recurrentes",
        tier=AlgorithmTier.PRECISION,
        min_months=24,
        min_records=730,
        category="forecast",
        icon="­ƒºá"
    ),
    AlgorithmSpec(
        id="prophet_forecast",
        name="Predicci├│n Prophet",
        description="Pron├│stico con detecci├│n autom├ítica de tendencias y festivos",
        tier=AlgorithmTier.PRECISION,
        min_months=18,
        min_records=500,
        category="forecast",
        icon="­ƒö«"
    ),
    AlgorithmSpec(
        id="bayesian_mmm",
        name="MMM Bayesiano",
        description="Modelado de medios con intervalos de confianza y priors",
        tier=AlgorithmTier.PRECISION,
        min_months=24,
        min_records=104,  # 2 a├▒os semanales
        category="mmm",
        icon="­ƒôÉ"
    ),
    AlgorithmSpec(
        id="causal_impact",
        name="Impacto Causal",
        description="Mide el efecto causal de intervenciones de marketing",
        tier=AlgorithmTier.PRECISION,
        min_months=24,
        min_records=365,
        category="mmm",
        icon="­ƒÄ»"
    ),
    
    # === TIER PRECISION (Continued) ===
    AlgorithmSpec(
        id="ltv_precision",
        name="LTV Precision (Kinetic)",
        description="Cinética de ingresos con Atención Temporal y XAI",
        tier=AlgorithmTier.PRECISION,
        min_months=24,
        min_records=1000,
        category="ltv",
        icon="🧠"
    ),
    AlgorithmSpec(
        id="mmm_precision",
        name="MMM Precision (Synergy 2.0)",
        description="Optimización Multi-Objetivo con Matriz de Sinergia Causal",
        tier=AlgorithmTier.PRECISION,
        min_months=24,
        min_records=104, # 2 años semanales
        category="mmm",
        icon="🎯"
    ),
    AlgorithmSpec(
        id="calibration_audit",
        name="Auditoría de Calibración",
        description="Verificación de integridad algorítmica y desviación de datos",
        tier=AlgorithmTier.PRECISION,
        min_months=12,
        min_records=500,
        category="ltv",
        icon="⚖️"
    ),
]
]


class AlgorithmTierService:
    """
    Servicio para gestionar algoritmos y tiers.
    
    Uso:
        service = AlgorithmTierService()
        unlocked = service.get_unlocked_algorithms(months=12, records=500)
        all_status = service.get_all_algorithms_status(months=12, records=500)
    """
    
    def __init__(self):
        self.catalog = ALGORITHM_CATALOG
    
    def get_all_algorithms(self) -> List[AlgorithmSpec]:
        """Retorna todos los algoritmos del cat├ílogo"""
        return self.catalog
    
    def get_algorithms_by_tier(self, tier: AlgorithmTier) -> List[AlgorithmSpec]:
        """Retorna algoritmos de un tier espec├¡fico"""
        return [a for a in self.catalog if a.tier == tier]
    
    def get_algorithms_by_category(self, category: str) -> List[AlgorithmSpec]:
        """Retorna algoritmos de una categor├¡a"""
        return [a for a in self.catalog if a.category == category]
    
    def get_unlocked_algorithms(self, months: int, records: int) -> List[AlgorithmSpec]:
        """Retorna algoritmos desbloqueados seg├║n datos disponibles"""
        return [a for a in self.catalog if a.is_unlocked(months, records)]
    
    def get_locked_algorithms(self, months: int, records: int) -> List[AlgorithmSpec]:
        """Retorna algoritmos bloqueados"""
        return [a for a in self.catalog if not a.is_unlocked(months, records)]
    
    def count_algorithms_by_data(self, months: int, records: int) -> Tuple[int, int]:
        """Cuenta algoritmos desbloqueados y bloqueados"""
        unlocked = len(self.get_unlocked_algorithms(months, records))
        locked = len(self.catalog) - unlocked
        return unlocked, locked
    
    def get_current_tier(self, months: int, records: int) -> AlgorithmTier:
        """Determina el tier actual seg├║n datos"""
        if months >= 24 and records >= 500:
            return AlgorithmTier.PRECISION
        elif months >= 12 and records >= 100:
            return AlgorithmTier.OPTIMISATION
        else:
            return AlgorithmTier.INTELLIGENCE
    
    def get_next_tier_requirements(self, months: int, records: int) -> Optional[Dict[str, Any]]:
        """Retorna requisitos para el siguiente tier"""
        current = self.get_current_tier(months, records)
        
        tier_requirements = {
            AlgorithmTier.INTELLIGENCE: {"tier": "OPTIMISATION", "min_months": 3, "min_records": 100},
            AlgorithmTier.OPTIMISATION: {"tier": "PRECISION", "min_months": 12, "min_records": 500},
            AlgorithmTier.PRECISION: None
        }
        
        next_req = tier_requirements[current]
        if not next_req:
            return None
        
        return {
            "next_tier": next_req["tier"],
            "months_needed": max(0, next_req["min_months"] - months),
            "records_needed": max(0, next_req["min_records"] - records),
        }
    
    def get_all_algorithms_status(self, months: int, records: int) -> Dict[str, Any]:
        """Retorna estado completo de todos los algoritmos para API"""
        unlocked = self.get_unlocked_algorithms(months, records)
        locked = self.get_locked_algorithms(months, records)
        current_tier = self.get_current_tier(months, records)
        next_tier = self.get_next_tier_requirements(months, records)
        
        # Agrupar por categor├¡a
        by_category = {}
        for algo in self.catalog:
            cat = algo.category
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(algo.to_dict(months, records))
        
        return {
            "current_tier": current_tier.value,
            "data_profile": {
                "months": months,
                "records": records,
            },
            "summary": {
                "total": len(self.catalog),
                "unlocked": len(unlocked),
                "locked": len(locked),
                "unlock_percentage": round((len(unlocked) / len(self.catalog)) * 100),
            },
            "next_tier": next_tier,
            "by_category": by_category,
            "unlocked_list": [a.to_dict(months, records) for a in unlocked],
            "locked_list": [a.to_dict(months, records) for a in locked],
        }


# Funci├│n de conveniencia
def get_algorithm_status(months: int, records: int) -> Dict[str, Any]:
    """Obtiene el estado de algoritmos para datos dados"""
    return AlgorithmTierService().get_all_algorithms_status(months, records)


# Tier labels para UI
TIER_LABELS = {
    AlgorithmTier.INTELLIGENCE: {
        "name": "Intelligence",
        "description": "LTV y segmentaci├│n predictiva esencial",
        "color": "blue",
        "icon": "­ƒôè",
    },
    AlgorithmTier.OPTIMISATION: {
        "name": "Optimisation",
        "description": "Optimizaci├│n de presupuesto y atribuci├│n avanzada",
        "color": "indigo",
        "icon": "ÔÜí",
    },
    AlgorithmTier.PRECISION: {
        "name": "Precision",
        "description": "IA Deep Learning para m├íxima exactitud",
        "color": "emerald",
        "icon": "­ƒºá",
    },
}
