"""
Mindbody Connector - Tactics
Integraci├│n con Mindbody Online API para gimnasios, yoga, pilates, spas.
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


class MindbodyConnector(FitnessConnector):
    """
    Conector para Mindbody Online - la plataforma m├ís usada en yoga/pilates/wellness.
    
    API Docs: https://developers.mindbodyonline.com/
    
    Endpoints principales:
    - /client/clients - Lista de clientes
    - /client/clientvisits - Historial de visitas
    - /sale/sales - Ventas y membres├¡as
    - /class/classes - Clases programadas
    
    Autenticaci├│n:
    - API Key (para acceso b├ísico)
    - OAuth 2.0 (para acceso en nombre de usuarios)
    """
    
    name = "Mindbody"
    BASE_URL = "https://api.mindbodyonline.com/public/v6"
    
    def __init__(
        self, 
        company_id: str,
        api_key: Optional[str] = None,
        site_id: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        force_mock: bool = False
    ):
        super().__init__(company_id, force_mock=force_mock)
        self.api_key = api_key or os.getenv("MINDBODY_API_KEY")
        self.site_id = site_id or os.getenv("MINDBODY_SITE_ID")
        self.username = username or os.getenv("MINDBODY_USERNAME")
        self.password = password or os.getenv("MINDBODY_PASSWORD")
        self._access_token: Optional[str] = None
        self._session = requests.Session()
    
    def authenticate(self) -> bool:
        """
        Autentica con Mindbody API.
        
        Usa username/password para obtener un user token,
        o API key para acceso b├ísico.
        """
        if not self.api_key:
            self.logger.error("MINDBODY_API_KEY not configured")
            return False
        
        if not self.site_id:
            self.logger.error("MINDBODY_SITE_ID not configured")
            return False
        
        # Set default headers
        self._session.headers.update({
            "Api-Key": self.api_key,
            "SiteId": self.site_id,
            "Content-Type": "application/json",
        })
        
        # If username/password provided, get user token
        if self.username and self.password:
            try:
                response = self._session.post(
                    f"{self.BASE_URL}/usertoken/issue",
                    json={
                        "Username": self.username,
                        "Password": self.password,
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    self._access_token = data.get("AccessToken")
                    self._session.headers["Authorization"] = f"Bearer {self._access_token}"
                    self.logger.info("Mindbody authentication successful (user token)")
                    return True
                else:
                    self.logger.warning(f"User token auth failed: {response.status_code}")
                    # Continue with API key only
                    
            except Exception as e:
                self.logger.warning(f"User token auth error: {e}")
        
        # Test API key access
        try:
            response = self._session.get(f"{self.BASE_URL}/site/sites")
            if response.status_code == 200:
                self.logger.info("Mindbody authentication successful (API key)")
                return True
            else:
                self.logger.error(f"API key auth failed: {response.status_code}")
                return False
        except Exception as e:
            self.logger.error(f"Authentication error: {e}")
            return False
    
    def get_members(self, updated_since: Optional[datetime] = None) -> List[Member]:
        """
        Obtiene clientes desde Mindbody.
        
        Endpoint: GET /client/clients
        """
        members = []
        
        try:
            params = {
                "Limit": 200,
                "Offset": 0,
            }
            
            if updated_since:
                params["LastModifiedDate"] = updated_since.isoformat()
            
            while True:
                response = self._session.get(
                    f"{self.BASE_URL}/client/clients",
                    params=params
                )
                
                if response.status_code != 200:
                    self.logger.error(f"Failed to get clients: {response.status_code}")
                    break
                
                data = response.json()
                clients = data.get("Clients", [])
                
                if not clients:
                    break
                
                for client in clients:
                    members.append(self._parse_client(client))
                
                # Pagination
                params["Offset"] += len(clients)
                if len(clients) < params["Limit"]:
                    break
            
            self.logger.info(f"Fetched {len(members)} members from Mindbody")
            return members
            
        except Exception as e:
            self.logger.error(f"Error fetching members: {e}")
            return self._mock_members() if not members else members
    
    def get_attendance(
        self, 
        start_date: date, 
        end_date: date,
        member_id: Optional[str] = None
    ) -> List[Attendance]:
        """
        Obtiene historial de visitas/check-ins.
        
        Endpoint: GET /client/clientvisits
        """
        attendance = []
        
        try:
            params = {
                "StartDate": start_date.isoformat(),
                "EndDate": end_date.isoformat(),
                "Limit": 200,
                "Offset": 0,
            }
            
            if member_id:
                params["ClientId"] = member_id
            
            while True:
                response = self._session.get(
                    f"{self.BASE_URL}/client/clientvisits",
                    params=params
                )
                
                if response.status_code != 200:
                    self.logger.error(f"Failed to get visits: {response.status_code}")
                    break
                
                data = response.json()
                visits = data.get("Visits", [])
                
                if not visits:
                    break
                
                for visit in visits:
                    attendance.append(self._parse_visit(visit))
                
                params["Offset"] += len(visits)
                if len(visits) < params["Limit"]:
                    break
            
            self.logger.info(f"Fetched {len(attendance)} attendance records from Mindbody")
            return attendance
            
        except Exception as e:
            self.logger.error(f"Error fetching attendance: {e}")
            return self._mock_attendance(start_date, end_date)
    
    def get_memberships(self, active_only: bool = False) -> List[Membership]:
        """
        Obtiene membres├¡as/contratos de clientes.
        
        Endpoint: GET /client/clientcontracts o /sale/contracts
        """
        memberships = []
        
        try:
            params = {
                "Limit": 200,
                "Offset": 0,
            }
            
            while True:
                response = self._session.get(
                    f"{self.BASE_URL}/sale/contracts",
                    params=params
                )
                
                if response.status_code != 200:
                    self.logger.error(f"Failed to get contracts: {response.status_code}")
                    break
                
                data = response.json()
                contracts = data.get("Contracts", [])
                
                if not contracts:
                    break
                
                for contract in contracts:
                    membership = self._parse_contract(contract)
                    if active_only and not membership.is_active:
                        continue
                    memberships.append(membership)
                
                params["Offset"] += len(contracts)
                if len(contracts) < params["Limit"]:
                    break
            
            self.logger.info(f"Fetched {len(memberships)} memberships from Mindbody")
            return memberships
            
        except Exception as e:
            self.logger.error(f"Error fetching memberships: {e}")
            return []
    
    def get_classes(
        self, 
        start_date: date, 
        end_date: date
    ) -> List[ClassSession]:
        """
        Obtiene clases programadas.
        
        Endpoint: GET /class/classes
        """
        classes = []
        
        try:
            params = {
                "StartDateTime": datetime.combine(start_date, datetime.min.time()).isoformat(),
                "EndDateTime": datetime.combine(end_date, datetime.max.time()).isoformat(),
                "Limit": 200,
                "Offset": 0,
            }
            
            while True:
                response = self._session.get(
                    f"{self.BASE_URL}/class/classes",
                    params=params
                )
                
                if response.status_code != 200:
                    self.logger.error(f"Failed to get classes: {response.status_code}")
                    break
                
                data = response.json()
                class_list = data.get("Classes", [])
                
                if not class_list:
                    break
                
                for cls in class_list:
                    classes.append(self._parse_class(cls))
                
                params["Offset"] += len(class_list)
                if len(class_list) < params["Limit"]:
                    break
            
            self.logger.info(f"Fetched {len(classes)} classes from Mindbody")
            return classes
            
        except Exception as e:
            self.logger.error(f"Error fetching classes: {e}")
            return self._mock_classes(start_date, end_date)
    
    # === PARSING METHODS ===
    
    def _parse_client(self, data: Dict) -> Member:
        """Parsea un cliente de Mindbody a Member"""
        status_map = {
            "Active": MembershipStatus.ACTIVE,
            "Inactive": MembershipStatus.CANCELLED,
            "Suspended": MembershipStatus.PAUSED,
        }
        
        return Member(
            id=str(data.get("Id", "")),
            email=data.get("Email", ""),
            first_name=data.get("FirstName", ""),
            last_name=data.get("LastName", ""),
            phone=data.get("MobilePhone") or data.get("HomePhone"),
            signup_date=datetime.fromisoformat(data["FirstAppointmentDate"]) if data.get("FirstAppointmentDate") else None,
            membership_status=status_map.get(data.get("Status"), MembershipStatus.ACTIVE),
            membership_type=data.get("ClientCreditCard", {}).get("ContractName"),
            tags=[r.get("Name") for r in data.get("ClientRelationships", []) if r.get("Name")],
        )
    
    def _parse_visit(self, data: Dict) -> Attendance:
        """Parsea una visita de Mindbody a Attendance"""
        return Attendance(
            id=str(data.get("Id", "")),
            member_id=str(data.get("ClientId", "")),
            date=datetime.fromisoformat(data["StartDateTime"]) if data.get("StartDateTime") else datetime.now(),
            class_name=data.get("Name", ""),
            class_type=data.get("ClassDescription", {}).get("SessionType", {}).get("Name", "general"),
            instructor=data.get("Staff", {}).get("Name"),
            location=data.get("Location", {}).get("Name"),
            duration_minutes=data.get("ClassDescription", {}).get("Duration"),
            checked_in=data.get("SignedIn", False),
            no_show=not data.get("SignedIn", True) and not data.get("LateCancelled", False),
        )
    
    def _parse_contract(self, data: Dict) -> Membership:
        """Parsea un contrato de Mindbody a Membership"""
        plan_map = {
            "Monthly": MembershipPlan.MONTHLY,
            "Quarterly": MembershipPlan.QUARTERLY,
            "Annual": MembershipPlan.ANNUAL,
            "Yearly": MembershipPlan.ANNUAL,
        }
        
        status_map = {
            "Active": MembershipStatus.ACTIVE,
            "Cancelled": MembershipStatus.CANCELLED,
            "Expired": MembershipStatus.EXPIRED,
        }
        
        autopay_schedule = data.get("AutopaySchedule", {})
        
        return Membership(
            id=str(data.get("Id", "")),
            member_id=str(data.get("ClientId", "")),
            plan_name=data.get("Name", ""),
            plan_type=plan_map.get(data.get("ContractTerms"), MembershipPlan.MONTHLY),
            price=float(autopay_schedule.get("Amount", 0)),
            currency="USD",  # Mindbody default
            start_date=datetime.fromisoformat(data["AgreementDate"]) if data.get("AgreementDate") else None,
            end_date=datetime.fromisoformat(data["EndDate"]) if data.get("EndDate") else None,
            next_billing_date=datetime.fromisoformat(autopay_schedule["RunDate"]) if autopay_schedule.get("RunDate") else None,
            status=status_map.get(data.get("Status"), MembershipStatus.ACTIVE),
            auto_renew=data.get("AutoRenew", True),
        )
    
    def _parse_class(self, data: Dict) -> ClassSession:
        """Parsea una clase de Mindbody a ClassSession"""
        return ClassSession(
            id=str(data.get("Id", "")),
            name=data.get("ClassDescription", {}).get("Name", ""),
            class_type=data.get("ClassDescription", {}).get("SessionType", {}).get("Name", "general"),
            instructor=data.get("Staff", {}).get("Name"),
            start_time=datetime.fromisoformat(data["StartDateTime"]) if data.get("StartDateTime") else None,
            end_time=datetime.fromisoformat(data["EndDateTime"]) if data.get("EndDateTime") else None,
            duration_minutes=data.get("ClassDescription", {}).get("Duration", 60),
            location=data.get("Location", {}).get("Name"),
            capacity=data.get("MaxCapacity", 20),
            booked_count=data.get("TotalBooked", 0),
            waitlist_count=data.get("TotalWaitlisted", 0),
            description=data.get("ClassDescription", {}).get("Description"),
        )
    
    # === MOCK METHODS FOR TESTING ===
    
    def _mock_members(self) -> List[Member]:
        """Miembros mock para testing"""
        return [
            Member(id="1001", email="elena@yogastudio.com", first_name="Elena", last_name="Rodr├¡guez", 
                   signup_date=datetime(2024, 1, 15), membership_type="Unlimited Yoga"),
            Member(id="1002", email="marcos@gym.com", first_name="Marcos", last_name="Garc├¡a",
                   signup_date=datetime(2024, 3, 1), membership_type="Monthly Premium"),
            Member(id="1003", email="sofia@pilates.com", first_name="Sof├¡a", last_name="Mart├¡n",
                   signup_date=datetime(2024, 6, 10), membership_type="Pay Per Class"),
        ]
    
    def _mock_attendance(self, start_date: date, end_date: date) -> List[Attendance]:
        """Asistencias mock para testing"""
        import random
        attendance = []
        members = ["1001", "1002", "1003"]
        class_types = ["yoga", "pilates", "spinning", "strength"]
        
        current = start_date
        att_id = 0
        while current <= end_date:
            for _ in range(random.randint(15, 25)):
                att_id += 1
                member = random.choice(members)
                attendance.append(Attendance(
                    id=str(att_id),
                    member_id=member,
                    date=datetime.combine(current, datetime.min.time().replace(hour=random.randint(7, 20))),
                    class_name=f"Clase {att_id}",
                    class_type=random.choice(class_types),
                    checked_in=random.random() > 0.1,
                    no_show=random.random() < 0.05,
                ))
            current += timedelta(days=1)
        
        return attendance
    
    def _mock_classes(self, start_date: date, end_date: date) -> List[ClassSession]:
        """Clases mock para testing"""
        classes = []
        current = start_date
        class_id = 0
        
        schedule = [
            (7, "Yoga Sunrise", "yoga", "Elena"),
            (9, "Power Pilates", "pilates", "Mar├¡a"),
            (10, "HIIT Extreme", "cardio", "Carlos"),
            (12, "Yoga Lunch", "yoga", "Elena"),
            (17, "Spinning Pro", "cardio", "Marcos"),
            (18, "Body Pump", "strength", "Pedro"),
            (19, "Yoga Relax", "yoga", "Sof├¡a"),
            (20, "Boxing Fit", "martial_arts", "Javier"),
        ]
        
        while current <= end_date:
            for hour, name, ctype, instructor in schedule:
                class_id += 1
                start_time = datetime.combine(current, datetime.min.time().replace(hour=hour))
                classes.append(ClassSession(
                    id=str(class_id),
                    name=name,
                    class_type=ctype,
                    instructor=instructor,
                    start_time=start_time,
                    end_time=start_time + timedelta(minutes=60),
                    duration_minutes=60,
                    capacity=20,
                    booked_count=15,
                ))
            current += timedelta(days=1)
        
        return classes
