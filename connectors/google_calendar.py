"""
Google Calendar Connector - Tactics
Para estudios peque├▒os que gestionan reservas/clases v├¡a Google Calendar.
"""

import os
from datetime import datetime, date, timedelta
from typing import List, Optional, Dict, Any
import logging

from .fitness_base import (
    FitnessConnector, Member, Attendance, Membership, ClassSession,
    MembershipStatus, MembershipPlan, FitnessSyncResult
)

logger = logging.getLogger(__name__)


class GoogleCalendarConnector(FitnessConnector):
    """
    Conector para estudios que usan Google Calendar para gestionar clases.
    
    Mapeo:
    - Eventos del calendario = Clases/Sesiones
    - Asistentes de eventos = Check-ins
    - Eventos recurrentes = Horarios regulares
    
    Requisitos:
    - Credenciales OAuth de Google Calendar API
    - Scope: https://www.googleapis.com/auth/calendar.readonly
    """
    
    name = "GoogleCalendar"
    
    def __init__(
        self, 
        company_id: str,
        credentials_path: Optional[str] = None,
        calendar_id: str = "primary",
        force_mock: bool = False
    ):
        super().__init__(company_id, force_mock=force_mock)
        self.credentials_path = credentials_path or os.getenv("GOOGLE_CREDENTIALS_PATH")
        self.calendar_id = calendar_id
        self._service = None
        self._members_cache: Dict[str, Member] = {}
    
    def authenticate(self) -> bool:
        """Autentica con Google Calendar API"""
        try:
            from google.oauth2.credentials import Credentials
            from google_auth_oauthlib.flow import InstalledAppFlow
            from google.auth.transport.requests import Request
            from googleapiclient.discovery import build
            import pickle
            
            SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
            
            creds = None
            token_path = f"tokens/google_calendar_{self.company_id}.pickle"
            
            # Load existing token
            if os.path.exists(token_path):
                with open(token_path, 'rb') as token:
                    creds = pickle.load(token)
            
            # Refresh or get new credentials
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    if not self.credentials_path or not os.path.exists(self.credentials_path):
                        self.logger.error("No credentials file found")
                        return False
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_path, SCOPES
                    )
                    creds = flow.run_local_server(port=0)
                
                # Save token
                os.makedirs("tokens", exist_ok=True)
                with open(token_path, 'wb') as token:
                    pickle.dump(creds, token)
            
            self._service = build('calendar', 'v3', credentials=creds)
            self.logger.info("Google Calendar authentication successful")
            return True
            
        except ImportError:
            self.logger.warning("Google API libraries not installed. Using mock mode.")
            return True  # Allow mock mode
        except Exception as e:
            self.logger.error(f"Authentication failed: {e}")
            return False
    
    def get_members(self, updated_since: Optional[datetime] = None) -> List[Member]:
        """
        Extrae miembros de los asistentes de eventos.
        
        En Google Calendar, los "miembros" son las personas que han asistido
        a eventos (clases) en el calendario.
        """
        # Return cached members if available
        if self._members_cache:
            return list(self._members_cache.values())
        
        # Extract members from attendance
        end = date.today()
        start = end - timedelta(days=90)
        attendance = self.get_attendance(start, end)
        
        # Los miembros se extraen de la cache poblada por get_attendance
        return list(self._members_cache.values())
    
    def get_attendance(
        self, 
        start_date: date, 
        end_date: date,
        member_id: Optional[str] = None
    ) -> List[Attendance]:
        """
        Obtiene asistencias desde eventos del calendario.
        
        Los asistentes de cada evento = check-ins de la clase.
        """
        if not self._service:
            # Mock mode for testing
            return self._mock_attendance(start_date, end_date)
        
        try:
            events_result = self._service.events().list(
                calendarId=self.calendar_id,
                timeMin=datetime.combine(start_date, datetime.min.time()).isoformat() + 'Z',
                timeMax=datetime.combine(end_date, datetime.max.time()).isoformat() + 'Z',
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            attendance_list = []
            
            for event in events:
                # Extract class info
                class_name = event.get('summary', 'Clase')
                class_type = self._detect_class_type(class_name)
                event_start = event.get('start', {}).get('dateTime')
                
                if not event_start:
                    continue
                
                event_datetime = datetime.fromisoformat(event_start.replace('Z', '+00:00'))
                
                # Extract attendees as check-ins
                attendees = event.get('attendees', [])
                for attendee in attendees:
                    email = attendee.get('email', '')
                    response = attendee.get('responseStatus', 'needsAction')
                    
                    if not email or '@' not in email:
                        continue
                    
                    # Create or update member
                    member_key = email.lower()
                    if member_key not in self._members_cache:
                        self._members_cache[member_key] = Member(
                            id=member_key,
                            email=email,
                            first_name=attendee.get('displayName', '').split()[0] if attendee.get('displayName') else '',
                            last_name=' '.join(attendee.get('displayName', '').split()[1:]) if attendee.get('displayName') else '',
                            signup_date=event_datetime,
                            membership_status=MembershipStatus.ACTIVE,
                        )
                    
                    # Filter by member_id if specified
                    if member_id and member_key != member_id:
                        continue
                    
                    # Create attendance record
                    attendance_list.append(Attendance(
                        id=f"{event.get('id', '')}_{member_key}",
                        member_id=member_key,
                        date=event_datetime,
                        class_name=class_name,
                        class_type=class_type,
                        checked_in=(response == 'accepted'),
                        no_show=(response == 'declined'),
                    ))
            
            return attendance_list
            
        except Exception as e:
            self.logger.error(f"Failed to get attendance: {e}")
            return []
    
    def get_memberships(self, active_only: bool = False) -> List[Membership]:
        """
        Google Calendar no tiene membres├¡as nativas.
        Retorna membres├¡as inferidas de la actividad.
        """
        members = self.get_members()
        memberships = []
        
        for member in members:
            memberships.append(Membership(
                id=f"gcal_{member.id}",
                member_id=member.id,
                plan_name="Google Calendar User",
                plan_type=MembershipPlan.PAY_PER_CLASS,
                price=0,
                start_date=member.signup_date,
                status=member.membership_status,
            ))
        
        return memberships
    
    def get_classes(
        self, 
        start_date: date, 
        end_date: date
    ) -> List[ClassSession]:
        """
        Obtiene clases desde eventos del calendario.
        """
        if not self._service:
            return self._mock_classes(start_date, end_date)
        
        try:
            events_result = self._service.events().list(
                calendarId=self.calendar_id,
                timeMin=datetime.combine(start_date, datetime.min.time()).isoformat() + 'Z',
                timeMax=datetime.combine(end_date, datetime.max.time()).isoformat() + 'Z',
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            classes = []
            
            for event in events:
                event_start = event.get('start', {}).get('dateTime')
                event_end = event.get('end', {}).get('dateTime')
                
                if not event_start:
                    continue
                
                start_dt = datetime.fromisoformat(event_start.replace('Z', '+00:00'))
                end_dt = datetime.fromisoformat(event_end.replace('Z', '+00:00')) if event_end else None
                
                duration = int((end_dt - start_dt).total_seconds() / 60) if end_dt else 60
                attendees = event.get('attendees', [])
                
                classes.append(ClassSession(
                    id=event.get('id', ''),
                    name=event.get('summary', 'Clase'),
                    class_type=self._detect_class_type(event.get('summary', '')),
                    instructor=event.get('organizer', {}).get('displayName'),
                    start_time=start_dt,
                    end_time=end_dt,
                    duration_minutes=duration,
                    location=event.get('location'),
                    capacity=20,  # Default
                    booked_count=len([a for a in attendees if a.get('responseStatus') == 'accepted']),
                    description=event.get('description'),
                ))
            
            return classes
            
        except Exception as e:
            self.logger.error(f"Failed to get classes: {e}")
            return []
    
    def _detect_class_type(self, name: str) -> str:
        """Detecta el tipo de clase desde el nombre"""
        name_lower = name.lower()
        
        type_keywords = {
            'yoga': ['yoga', 'vinyasa', 'hatha', 'ashtanga', 'yin'],
            'pilates': ['pilates', 'mat', 'reformer'],
            'cardio': ['cardio', 'hiit', 'spinning', 'cycling', 'zumba'],
            'strength': ['fuerza', 'strength', 'weights', 'pesas', 'crossfit'],
            'dance': ['baile', 'dance', 'salsa', 'bachata'],
            'martial_arts': ['boxeo', 'boxing', 'kickboxing', 'martial'],
            'wellness': ['meditaci├│n', 'meditation', 'mindfulness', 'relax'],
        }
        
        for class_type, keywords in type_keywords.items():
            if any(kw in name_lower for kw in keywords):
                return class_type
        
        return 'general'
    
    # === MOCK METHODS FOR TESTING ===
    
    def _mock_attendance(self, start_date: date, end_date: date) -> List[Attendance]:
        """Datos mock para testing"""
        import random
        
        mock_members = [
            ("maria@example.com", "Mar├¡a", "Garc├¡a"),
            ("carlos@example.com", "Carlos", "L├│pez"),
            ("ana@example.com", "Ana", "Mart├¡nez"),
            ("pedro@example.com", "Pedro", "S├ínchez"),
            ("laura@example.com", "Laura", "Fern├índez"),
        ]
        
        class_types = ['yoga', 'pilates', 'cardio', 'strength']
        attendance = []
        
        current = start_date
        while current <= end_date:
            # 2-3 classes per day
            for _ in range(random.randint(2, 3)):
                class_type = random.choice(class_types)
                class_time = datetime.combine(current, datetime.min.time().replace(
                    hour=random.choice([9, 10, 11, 17, 18, 19])
                ))
                
                # 3-8 attendees per class
                for email, first, last in random.sample(mock_members, random.randint(3, 5)):
                    if email not in self._members_cache:
                        self._members_cache[email] = Member(
                            id=email,
                            email=email,
                            first_name=first,
                            last_name=last,
                            signup_date=class_time - timedelta(days=random.randint(30, 180)),
                            membership_status=MembershipStatus.ACTIVE,
                        )
                    
                    attendance.append(Attendance(
                        id=f"mock_{current}_{class_type}_{email}",
                        member_id=email,
                        date=class_time,
                        class_name=f"Clase de {class_type.title()}",
                        class_type=class_type,
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
            (9, 'Yoga Matinal', 'yoga', 'Mar├¡a'),
            (10, 'Pilates Core', 'pilates', 'Carlos'),
            (11, 'HIIT Express', 'cardio', 'Ana'),
            (17, 'Yoga Flow', 'yoga', 'Mar├¡a'),
            (18, 'Spinning', 'cardio', 'Pedro'),
            (19, 'Fuerza Total', 'strength', 'Laura'),
        ]
        
        while current <= end_date:
            for hour, name, ctype, instructor in schedule:
                class_id += 1
                start_time = datetime.combine(current, datetime.min.time().replace(hour=hour))
                
                classes.append(ClassSession(
                    id=f"class_{class_id}",
                    name=name,
                    class_type=ctype,
                    instructor=instructor,
                    start_time=start_time,
                    end_time=start_time + timedelta(minutes=60),
                    duration_minutes=60,
                    capacity=15,
                    booked_count=10,
                ))
            
            current += timedelta(days=1)
        
        return classes
