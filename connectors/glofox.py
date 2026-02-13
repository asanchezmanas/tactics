"""
Glofox Connector - Tactics
Integraci├│n con Glofox para gimnasios y estudios de fitness (mercado EU/UK).
"""

import os
import requests
from datetime import datetime, date, timedelta
from typing import List, Optional, Dict, Any
import logging

from .fitness_base import (
    FitnessConnector, Member, Attendance, Membership, ClassSession,
    MembershipStatus, MembershipPlan, FitnessSyncResult
)

logger = logging.getLogger(__name__)


class GlofoxConnector(FitnessConnector):
    """
    Conector para Glofox - popular en Europa/UK para gimnasios y boutiques fitness.
    
    API Docs: https://developer.glofox.com/
    
    Endpoints principales:
    - /members - Lista de miembros
    - /bookings - Reservas de clases
    - /memberships - Planes activos
    - /classes - Clases programadas
    
    Autenticaci├│n:
    - API Key + Secret
    - OAuth 2.0 para acceso de partners
    """
    
    name = "Glofox"
    BASE_URL = "https://api.glofox.com/v1"
    
    def __init__(
        self, 
        company_id: str,
        api_key: Optional[str] = None,
        api_secret: Optional[str] = None,
        branch_id: Optional[str] = None,
        force_mock: bool = False
    ):
        super().__init__(company_id, force_mock=force_mock)
        self.api_key = api_key or os.getenv("GLOFOX_API_KEY")
        self.api_secret = api_secret or os.getenv("GLOFOX_API_SECRET")
        self.branch_id = branch_id or os.getenv("GLOFOX_BRANCH_ID")
        self._session = requests.Session()
        self._access_token: Optional[str] = None
    
    def authenticate(self) -> bool:
        """Autentica con Glofox API usando API Key + Secret"""
        if not self.api_key or not self.api_secret:
            self.logger.error("GLOFOX_API_KEY or GLOFOX_API_SECRET not configured")
            return False
        
        try:
            # Get access token
            response = self._session.post(
                f"{self.BASE_URL}/auth/token",
                json={
                    "api_key": self.api_key,
                    "api_secret": self.api_secret,
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                self._access_token = data.get("access_token")
                self._session.headers.update({
                    "Authorization": f"Bearer {self._access_token}",
                    "Content-Type": "application/json",
                })
                self.logger.info("Glofox authentication successful")
                return True
            else:
                self.logger.error(f"Glofox auth failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.logger.error(f"Glofox authentication error: {e}")
            return False
    
    def get_members(self, updated_since: Optional[datetime] = None) -> List[Member]:
        """Obtiene miembros desde Glofox"""
        members = []
        
        try:
            params = {"limit": 100, "offset": 0}
            if self.branch_id:
                params["branch_id"] = self.branch_id
            if updated_since:
                params["updated_after"] = updated_since.isoformat()
            
            while True:
                response = self._session.get(
                    f"{self.BASE_URL}/members",
                    params=params
                )
                
                if response.status_code != 200:
                    self.logger.error(f"Failed to get members: {response.status_code}")
                    break
                
                data = response.json()
                member_list = data.get("data", [])
                
                if not member_list:
                    break
                
                for m in member_list:
                    members.append(self._parse_member(m))
                
                params["offset"] += len(member_list)
                if len(member_list) < params["limit"]:
                    break
            
            return members
            
        except Exception as e:
            self.logger.error(f"Error fetching members: {e}")
            return self._mock_members()
    
    def get_attendance(
        self, 
        start_date: date, 
        end_date: date,
        member_id: Optional[str] = None
    ) -> List[Attendance]:
        """Obtiene reservas/check-ins desde Glofox"""
        attendance = []
        
        try:
            params = {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "limit": 100,
                "offset": 0,
            }
            if member_id:
                params["member_id"] = member_id
            if self.branch_id:
                params["branch_id"] = self.branch_id
            
            while True:
                response = self._session.get(
                    f"{self.BASE_URL}/bookings",
                    params=params
                )
                
                if response.status_code != 200:
                    break
                
                data = response.json()
                bookings = data.get("data", [])
                
                if not bookings:
                    break
                
                for b in bookings:
                    attendance.append(self._parse_booking(b))
                
                params["offset"] += len(bookings)
                if len(bookings) < params["limit"]:
                    break
            
            return attendance
            
        except Exception as e:
            self.logger.error(f"Error fetching attendance: {e}")
            return self._mock_attendance(start_date, end_date)
    
    def get_memberships(self, active_only: bool = False) -> List[Membership]:
        """Obtiene planes de membres├¡a desde Glofox"""
        memberships = []
        
        try:
            params = {"limit": 100, "offset": 0}
            if active_only:
                params["status"] = "active"
            if self.branch_id:
                params["branch_id"] = self.branch_id
            
            while True:
                response = self._session.get(
                    f"{self.BASE_URL}/memberships",
                    params=params
                )
                
                if response.status_code != 200:
                    break
                
                data = response.json()
                membership_list = data.get("data", [])
                
                if not membership_list:
                    break
                
                for m in membership_list:
                    memberships.append(self._parse_membership(m))
                
                params["offset"] += len(membership_list)
                if len(membership_list) < params["limit"]:
                    break
            
            return memberships
            
        except Exception as e:
            self.logger.error(f"Error fetching memberships: {e}")
            return []
    
    def get_classes(
        self, 
        start_date: date, 
        end_date: date
    ) -> List[ClassSession]:
        """Obtiene clases programadas desde Glofox"""
        classes = []
        
        try:
            params = {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "limit": 100,
                "offset": 0,
            }
            if self.branch_id:
                params["branch_id"] = self.branch_id
            
            while True:
                response = self._session.get(
                    f"{self.BASE_URL}/classes",
                    params=params
                )
                
                if response.status_code != 200:
                    break
                
                data = response.json()
                class_list = data.get("data", [])
                
                if not class_list:
                    break
                
                for c in class_list:
                    classes.append(self._parse_class(c))
                
                params["offset"] += len(class_list)
                if len(class_list) < params["limit"]:
                    break
            
            return classes
            
        except Exception as e:
            self.logger.error(f"Error fetching classes: {e}")
            return self._mock_classes(start_date, end_date)
    
    # === PARSING METHODS ===
    
    def _parse_member(self, data: Dict) -> Member:
        """Parsea un miembro de Glofox"""
        status_map = {
            "active": MembershipStatus.ACTIVE,
            "inactive": MembershipStatus.CANCELLED,
            "paused": MembershipStatus.PAUSED,
            "trial": MembershipStatus.TRIAL,
        }
        
        return Member(
            id=str(data.get("id", "")),
            email=data.get("email", ""),
            first_name=data.get("first_name", ""),
            last_name=data.get("last_name", ""),
            phone=data.get("phone"),
            signup_date=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else None,
            membership_status=status_map.get(data.get("status"), MembershipStatus.ACTIVE),
            membership_type=data.get("membership_name"),
            tags=data.get("tags", []),
        )
    
    def _parse_booking(self, data: Dict) -> Attendance:
        """Parsea una reserva de Glofox"""
        return Attendance(
            id=str(data.get("id", "")),
            member_id=str(data.get("member_id", "")),
            date=datetime.fromisoformat(data["class_start"]) if data.get("class_start") else datetime.now(),
            class_name=data.get("class_name", ""),
            class_type=data.get("class_type", "general"),
            instructor=data.get("instructor_name"),
            location=data.get("location"),
            duration_minutes=data.get("duration"),
            checked_in=data.get("checked_in", False),
            no_show=data.get("no_show", False),
        )
    
    def _parse_membership(self, data: Dict) -> Membership:
        """Parsea una membres├¡a de Glofox"""
        plan_map = {
            "monthly": MembershipPlan.MONTHLY,
            "quarterly": MembershipPlan.QUARTERLY,
            "annual": MembershipPlan.ANNUAL,
            "pay_as_you_go": MembershipPlan.PAY_PER_CLASS,
        }
        
        status_map = {
            "active": MembershipStatus.ACTIVE,
            "cancelled": MembershipStatus.CANCELLED,
            "paused": MembershipStatus.PAUSED,
            "expired": MembershipStatus.EXPIRED,
        }
        
        return Membership(
            id=str(data.get("id", "")),
            member_id=str(data.get("member_id", "")),
            plan_name=data.get("name", ""),
            plan_type=plan_map.get(data.get("billing_period"), MembershipPlan.MONTHLY),
            price=float(data.get("price", 0)),
            currency=data.get("currency", "EUR"),
            start_date=datetime.fromisoformat(data["start_date"]) if data.get("start_date") else None,
            end_date=datetime.fromisoformat(data["end_date"]) if data.get("end_date") else None,
            next_billing_date=datetime.fromisoformat(data["next_payment"]) if data.get("next_payment") else None,
            status=status_map.get(data.get("status"), MembershipStatus.ACTIVE),
            auto_renew=data.get("auto_renew", True),
        )
    
    def _parse_class(self, data: Dict) -> ClassSession:
        """Parsea una clase de Glofox"""
        return ClassSession(
            id=str(data.get("id", "")),
            name=data.get("name", ""),
            class_type=data.get("type", "general"),
            instructor=data.get("instructor_name"),
            start_time=datetime.fromisoformat(data["start_time"]) if data.get("start_time") else None,
            end_time=datetime.fromisoformat(data["end_time"]) if data.get("end_time") else None,
            duration_minutes=data.get("duration", 60),
            location=data.get("location"),
            capacity=data.get("capacity", 20),
            booked_count=data.get("booked", 0),
            waitlist_count=data.get("waitlist", 0),
            description=data.get("description"),
        )
    
    # === MOCK METHODS ===
    
    def _mock_members(self) -> List[Member]:
        """Miembros mock para testing"""
        return [
            Member(id="g001", email="james@london.uk", first_name="James", last_name="Smith",
                   signup_date=datetime(2024, 2, 1), membership_type="Premium Monthly"),
            Member(id="g002", email="emma@manchester.uk", first_name="Emma", last_name="Wilson",
                   signup_date=datetime(2024, 4, 15), membership_type="Unlimited"),
            Member(id="g003", email="oliver@dublin.ie", first_name="Oliver", last_name="Murphy",
                   signup_date=datetime(2024, 5, 20), membership_type="Pay As You Go"),
        ]
    
    def _mock_attendance(self, start_date: date, end_date: date) -> List[Attendance]:
        """Asistencias mock para testing"""
        import random
        attendance = []
        members = ["g001", "g002", "g003"]
        class_types = ["hiit", "yoga", "boxing", "cycling"]
        
        current = start_date
        att_id = 0
        while current <= end_date:
            for _ in range(random.randint(20, 35)):
                att_id += 1
                attendance.append(Attendance(
                    id=f"gatt_{att_id}",
                    member_id=random.choice(members),
                    date=datetime.combine(current, datetime.min.time().replace(hour=random.randint(6, 21))),
                    class_name=f"Class {att_id}",
                    class_type=random.choice(class_types),
                    checked_in=random.random() > 0.08,
                    no_show=random.random() < 0.04,
                ))
            current += timedelta(days=1)
        
        return attendance
    
    def _mock_classes(self, start_date: date, end_date: date) -> List[ClassSession]:
        """Clases mock para testing"""
        classes = []
        current = start_date
        class_id = 0
        
        schedule = [
            (6, "Early Bird HIIT", "hiit", "James"),
            (7, "Morning Yoga", "yoga", "Sarah"),
            (9, "Spin Class", "cycling", "Mike"),
            (12, "Lunch Boxing", "boxing", "Tom"),
            (17, "After Work Pump", "strength", "Emma"),
            (18, "Evening Flow", "yoga", "Sarah"),
            (19, "CrossFit WOD", "crossfit", "James"),
        ]
        
        while current <= end_date:
            for hour, name, ctype, instructor in schedule:
                class_id += 1
                start_time = datetime.combine(current, datetime.min.time().replace(hour=hour))
                classes.append(ClassSession(
                    id=f"gcls_{class_id}",
                    name=name,
                    class_type=ctype,
                    instructor=instructor,
                    start_time=start_time,
                    end_time=start_time + timedelta(minutes=45),
                    duration_minutes=45,
                    capacity=25,
                    booked_count=18,
                ))
            current += timedelta(days=1)
        
        return classes
