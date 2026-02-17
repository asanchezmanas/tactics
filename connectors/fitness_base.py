"""
Fitness & Wellness Connector Base - Tactics
Base classes and data models for gym, yoga, pilates, and wellness integrations.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, date
from enum import Enum
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


# === DATA MODELS ===

class MembershipStatus(Enum):
    """Estado de membres├¡a"""
    ACTIVE = "active"
    PAUSED = "paused"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    TRIAL = "trial"


class MembershipPlan(Enum):
    """Tipos comunes de planes"""
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    ANNUAL = "annual"
    PAY_PER_CLASS = "pay_per_class"
    UNLIMITED = "unlimited"
    TRIAL = "trial"


@dataclass
class Member:
    """
    Representa un socio/cliente del gimnasio o estudio.
    
    Campos mapeados desde cualquier plataforma (Mindbody, Glofox, etc.)
    """
    id: str
    email: str
    first_name: str = ""
    last_name: str = ""
    phone: Optional[str] = None
    signup_date: Optional[datetime] = None
    membership_status: MembershipStatus = MembershipStatus.ACTIVE
    membership_type: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    custom_fields: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "email": self.email,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "full_name": self.full_name,
            "phone": self.phone,
            "signup_date": self.signup_date.isoformat() if self.signup_date else None,
            "membership_status": self.membership_status.value,
            "membership_type": self.membership_type,
            "tags": self.tags,
        }
    
    def to_tactics_row(self) -> Dict[str, Any]:
        """Convierte a formato para inserci├│n en Tactics DB"""
        return {
            "customer_id": self.id,
            "email": self.email,
            "name": self.full_name,
            "first_purchase_date": self.signup_date.isoformat() if self.signup_date else None,
            "segment": self.membership_type or "standard",
        }


@dataclass
class Attendance:
    """
    Representa una asistencia/check-in a una clase o instalaci├│n.
    """
    id: str
    member_id: str
    date: datetime
    class_name: Optional[str] = None
    class_type: Optional[str] = None  # yoga, pilates, cardio, etc.
    instructor: Optional[str] = None
    location: Optional[str] = None
    duration_minutes: Optional[int] = None
    checked_in: bool = True
    no_show: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "member_id": self.member_id,
            "date": self.date.isoformat(),
            "class_name": self.class_name,
            "class_type": self.class_type,
            "instructor": self.instructor,
            "location": self.location,
            "duration_minutes": self.duration_minutes,
            "checked_in": self.checked_in,
            "no_show": self.no_show,
        }
    
    def to_tactics_row(self) -> Dict[str, Any]:
        """Convierte a formato venta para LTV/Churn analysis"""
        return {
            "id": self.id,
            "customer_id": self.member_id,
            "order_date": self.date.isoformat(),
            "revenue": 0,  # Las asistencias no tienen revenue directo
            "channel": self.class_type or "gym",
        }


@dataclass
class Membership:
    """
    Representa una membres├¡a/suscripci├│n activa o hist├│rica.
    """
    id: str
    member_id: str
    plan_name: str
    plan_type: MembershipPlan = MembershipPlan.MONTHLY
    price: float = 0.0
    currency: str = "EUR"
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    next_billing_date: Optional[datetime] = None
    status: MembershipStatus = MembershipStatus.ACTIVE
    auto_renew: bool = True
    payment_method: Optional[str] = None
    
    @property
    def is_active(self) -> bool:
        return self.status == MembershipStatus.ACTIVE
    
    @property
    def monthly_value(self) -> float:
        """Calcula valor mensual equivalente"""
        if self.plan_type == MembershipPlan.ANNUAL:
            return self.price / 12
        elif self.plan_type == MembershipPlan.QUARTERLY:
            return self.price / 3
        return self.price
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "member_id": self.member_id,
            "plan_name": self.plan_name,
            "plan_type": self.plan_type.value,
            "price": self.price,
            "currency": self.currency,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "status": self.status.value,
            "auto_renew": self.auto_renew,
            "monthly_value": self.monthly_value,
        }
    
    def to_tactics_row(self) -> Dict[str, Any]:
        """Convierte a formato venta para LTV analysis"""
        return {
            "id": f"membership_{self.id}",
            "customer_id": self.member_id,
            "order_date": self.start_date.isoformat() if self.start_date else None,
            "revenue": self.price,
            "channel": "membership",
        }


@dataclass
class ClassSession:
    """
    Representa una clase programada (yoga, spinning, etc.)
    """
    id: str
    name: str
    class_type: str
    instructor: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration_minutes: int = 60
    location: Optional[str] = None
    capacity: int = 20
    booked_count: int = 0
    waitlist_count: int = 0
    description: Optional[str] = None
    
    @property
    def availability(self) -> int:
        return max(0, self.capacity - self.booked_count)
    
    @property
    def fill_rate(self) -> float:
        if self.capacity == 0:
            return 0
        return (self.booked_count / self.capacity) * 100
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "class_type": self.class_type,
            "instructor": self.instructor,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration_minutes": self.duration_minutes,
            "location": self.location,
            "capacity": self.capacity,
            "booked_count": self.booked_count,
            "availability": self.availability,
            "fill_rate": round(self.fill_rate, 1),
        }


# === SYNC RESULT ===

@dataclass
class FitnessSyncResult:
    """Resultado de una sincronizaci├│n"""
    success: bool
    connector_name: str
    members_synced: int = 0
    attendance_synced: int = 0
    memberships_synced: int = 0
    classes_synced: int = 0
    errors: List[str] = field(default_factory=list)
    sync_duration_seconds: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "connector": self.connector_name,
            "synced": {
                "members": self.members_synced,
                "attendance": self.attendance_synced,
                "memberships": self.memberships_synced,
                "classes": self.classes_synced,
            },
            "errors": self.errors,
            "duration_seconds": round(self.sync_duration_seconds, 2),
        }


# === ABSTRACT BASE CLASS ===

class FitnessConnector(ABC):
    """
    Clase base abstracta para todos los conectores de Fitness & Wellness.
    
    Implementa el patr├│n com├║n de sincronizaci├│n para gimnasios, estudios de yoga,
    pilates, y otros negocios de servicios recurrentes.
    
    Subclases deben implementar:
    - get_members()
    - get_attendance()
    - get_memberships()
    - get_classes()
    """
    
    name: str = "FitnessConnector"
    
    def __init__(self, company_id: str, force_mock: bool = False):
        self.company_id = company_id
        self.force_mock = force_mock
        self.logger = logging.getLogger(f"connector.{self.name}")
    
    # === ABSTRACT METHODS (must implement) ===
    
    @abstractmethod
    def authenticate(self) -> bool:
        """Autentica con la API del servicio"""
        pass
    
    @abstractmethod
    def get_members(self, updated_since: Optional[datetime] = None) -> List[Member]:
        """
        Obtiene lista de socios/miembros.
        
        Args:
            updated_since: Solo socios actualizados despu├®s de esta fecha (para sync incremental)
            
        Returns:
            Lista de objetos Member
        """
        pass
    
    @abstractmethod
    def get_attendance(
        self, 
        start_date: date, 
        end_date: date,
        member_id: Optional[str] = None
    ) -> List[Attendance]:
        """
        Obtiene historial de asistencias/check-ins.
        
        Args:
            start_date: Fecha inicio del per├¡odo
            end_date: Fecha fin del per├¡odo
            member_id: Opcional, filtrar por socio espec├¡fico
            
        Returns:
            Lista de objetos Attendance
        """
        pass
    
    @abstractmethod
    def get_memberships(self, active_only: bool = False) -> List[Membership]:
        """
        Obtiene membres├¡as/suscripciones.
        
        Args:
            active_only: Si True, solo membres├¡as activas
            
        Returns:
            Lista de objetos Membership
        """
        pass
    
    @abstractmethod
    def get_classes(
        self, 
        start_date: date, 
        end_date: date
    ) -> List[ClassSession]:
        """
        Obtiene clases programadas.
        
        Args:
            start_date: Fecha inicio
            end_date: Fecha fin
            
        Returns:
            Lista de objetos ClassSession
        """
        pass
    
    # === COMMON METHODS ===
    
    def full_sync(self, days_back: int = 90) -> FitnessSyncResult:
        """
        Sincronizaci├│n completa de todos los datos.
        
        Args:
            days_back: D├¡as hacia atr├ís para sincronizar asistencias
        """
        import time
        start_time = time.time()
        
        result = FitnessSyncResult(
            success=True,
            connector_name=self.name
        )
        
        try:
            # 1. Authenticate (bypass if force_mock)
            if self.force_mock:
                self.logger.info(f"Using mock mode for {self.name}")
            elif not self.authenticate():
                result.success = False
                result.errors.append("Authentication failed")
                return result
            
            # 2. Sync members
            self.logger.info("Syncing members...")
            members = self.get_members() if not self.force_mock else self._mock_members()
            result.members_synced = len(members)
            
            # 3. Sync memberships
            self.logger.info("Syncing memberships...")
            memberships = self.get_memberships() if not self.force_mock else self._mock_memberships()
            result.memberships_synced = len(memberships)
            
            # 4. Sync attendance
            self.logger.info(f"Syncing attendance ({days_back} days)...")
            end_date = date.today()
            start_date = date.today() - timedelta(days=days_back)
            attendance = self.get_attendance(start_date, end_date) if not self.force_mock else self._mock_attendance(start_date, end_date)
            result.attendance_synced = len(attendance)
            
            # 5. Sync classes
            self.logger.info("Syncing classes...")
            classes = self.get_classes(start_date, end_date) if not self.force_mock else self._mock_classes(start_date, end_date)
            result.classes_synced = len(classes)
            
        except Exception as e:
            result.success = False
            result.errors.append(str(e))
            self.logger.error(f"Sync failed: {e}")
        
        result.sync_duration_seconds = time.time() - start_time
        return result
    
    def get_member_stats(self, member_id: str, days: int = 30) -> Dict[str, Any]:
        """Obtiene estad├¡sticas de un socio espec├¡fico"""
        end = date.today()
        start = end - timedelta(days=days)
        
        attendance = self.get_attendance(start, end, member_id=member_id)
        
        return {
            "member_id": member_id,
            "period_days": days,
            "total_visits": len(attendance),
            "visits_per_week": len(attendance) / (days / 7),
            "class_types": list(set(a.class_type for a in attendance if a.class_type)),
            "no_shows": sum(1 for a in attendance if a.no_show),
        }
    
    def get_churn_risk_members(self, inactive_days: int = 21) -> List[Member]:
        """
        Identifica socios en riesgo de churn (no asistencia reciente).
        
        Args:
            inactive_days: D├¡as sin asistencia para considerar en riesgo
        """
        members = self.get_members()
        end = date.today()
        start = end - timedelta(days=inactive_days)
        
        # Get all attendance in period
        all_attendance = self.get_attendance(start, end)
        active_member_ids = set(a.member_id for a in all_attendance)
        
        # Filter to members who haven't attended
        at_risk = [m for m in members if m.id not in active_member_ids 
                   and m.membership_status == MembershipStatus.ACTIVE]
        
        return at_risk

    # === DEFAULT MOCK METHODS ===
    
    def _mock_members(self) -> List[Member]:
        """Default mock members"""
        return []
        
    def _mock_attendance(self, start_date: date, end_date: date) -> List[Attendance]:
        """Default mock attendance"""
        return []
        
    def _mock_memberships(self) -> List[Membership]:
        """Default mock memberships"""
        return []
        
    def _mock_classes(self, start_date: date, end_date: date) -> List[ClassSession]:
        """Default mock classes"""
        return []


# Import timedelta for full_sync
from datetime import timedelta
