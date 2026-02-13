"""
Stripe Fitness Connector - Tactics
Mapeo de suscripciones de Stripe a modelos de membres├¡a para Fitness/Wellness.
"""

import os
import stripe
from datetime import datetime, date, timedelta
from typing import List, Optional, Dict, Any
import logging

from .fitness_base import (
    FitnessConnector, Member, Attendance, Membership, ClassSession,
    MembershipStatus, MembershipPlan, FitnessSyncResult
)

logger = logging.getLogger(__name__)


class StripeFitnessConnector(FitnessConnector):
    """
    Conector de Stripe adaptado para negocios de Fitness.
    
    Transforma suscripciones de Stripe en objetos Membership de Tactics.
    ├Ütil para gimnasios y estudios que usan Stripe Billing directamente.
    """
    
    name = "StripeFitness"
    
    def __init__(self, company_id: str, api_key: Optional[str] = None, force_mock: bool = False):
        super().__init__(company_id, force_mock=force_mock)
        self.api_key = api_key or os.getenv("STRIPE_API_KEY")
        if self.api_key:
            stripe.api_key = self.api_key
    
    def authenticate(self) -> bool:
        """Verifica la validez de la API Key de Stripe"""
        if not self.api_key:
            self.logger.error("STRIPE_API_KEY not configured")
            return False
        
        try:
            stripe.Account.retrieve()
            self.logger.info("Stripe authentication successful")
            return True
        except Exception as e:
            self.logger.error(f"Stripe authentication failed: {e}")
            return False
    
    def get_members(self, updated_since: Optional[datetime] = None) -> List[Member]:
        """Obtiene clientes de Stripe y los mapea a Member"""
        members = []
        try:
            params = {"limit": 100}
            if updated_since:
                # Stripe uses unix timestamp
                params["created"] = {"gt": int(updated_since.timestamp())}
            
            customers = stripe.Customer.list(**params)
            for cust in customers.auto_paging_iter():
                members.append(Member(
                    id=cust.id,
                    email=cust.email or "",
                    first_name=cust.name.split()[0] if cust.name else "",
                    last_name=" ".join(cust.name.split()[1:]) if cust.name else "",
                    signup_date=datetime.fromtimestamp(cust.created),
                    membership_status=MembershipStatus.ACTIVE, # Default
                ))
            return members
        except Exception as e:
            self.logger.error(f"Error fetching Stripe customers: {e}")
            return self._mock_members()
    
    def get_memberships(self, active_only: bool = False) -> List[Membership]:
        """Mapea suscripciones de Stripe a Membership"""
        memberships = []
        try:
            params = {"limit": 100, "expand": ["data.customer", "data.plan.product"]}
            if active_only:
                params["status"] = "active"
            
            subscriptions = stripe.Subscription.list(**params)
            for sub in subscriptions.auto_paging_iter():
                memberships.append(self._parse_subscription(sub))
            
            return memberships
        except Exception as e:
            self.logger.error(f"Error fetching Stripe subscriptions: {e}")
            return []
    
    def get_attendance(
        self, 
        start_date: date, 
        end_date: date,
        member_id: Optional[str] = None
    ) -> List[Attendance]:
        """
        Stripe no tiene datos de asistencia de forma nativa. 
        Este m├®todo podr├¡a integrarse con Stripe Terminal o webhooks de check-in externos.
        """
        self.logger.warning("Stripe does not provide native attendance data.")
        return []
    
    def get_classes(self, start_date: date, end_date: date) -> List[ClassSession]:
        """Stripe no tiene datos de clases programadas."""
        return []
    
    def _parse_subscription(self, sub: Any) -> Membership:
        """Parsea una suscripci├│n de Stripe a Membership"""
        # Determinar el tipo de plan seg├║n el intervalo
        interval = sub.plan.interval
        interval_count = sub.plan.interval_count
        
        plan_type = MembershipPlan.MONTHLY
        if interval == "year":
            plan_type = MembershipPlan.ANNUAL
        elif interval == "month" and interval_count == 3:
            plan_type = MembershipPlan.QUARTERLY
        
        # Mapear estado
        status_map = {
            "active": MembershipStatus.ACTIVE,
            "past_due": MembershipStatus.PAUSED,
            "unpaid": MembershipStatus.PAUSED,
            "canceled": MembershipStatus.CANCELLED,
            "incomplete": MembershipStatus.TRIAL,
            "trialing": MembershipStatus.TRIAL,
        }
        
        return Membership(
            id=sub.id,
            member_id=sub.customer.id if hasattr(sub.customer, 'id') else sub.customer,
            plan_name=sub.plan.product.name if hasattr(sub.plan.product, 'name') else "Standard Plan",
            plan_type=plan_type,
            price=sub.plan.amount / 100.0,
            currency=sub.plan.currency.upper(),
            start_date=datetime.fromtimestamp(sub.start_date),
            end_date=datetime.fromtimestamp(sub.current_period_end),
            status=status_map.get(sub.status, MembershipStatus.ACTIVE),
            auto_renew=not sub.cancel_at_period_end,
        )
    
    def _mock_memberships(self) -> List[Membership]:
        """Membres├¡as mock para testing"""
        return [
            Membership(id="sub_1", member_id="cus_1", plan_name="Premium Yoga", 
                       plan_type=MembershipPlan.ANNUAL, price=1200, currency="EUR",
                       start_date=datetime.now() - timedelta(days=60), status=MembershipStatus.ACTIVE),
            Membership(id="sub_2", member_id="cus_1", plan_name="Monthly Mat", 
                       plan_type=MembershipPlan.MONTHLY, price=80, currency="EUR",
                       start_date=datetime.now() - timedelta(days=30), status=MembershipStatus.ACTIVE),
        ]
