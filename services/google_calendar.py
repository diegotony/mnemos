"""
Servicio para interactuar con Google Calendar API.
Basado en Service Account authentication.
"""

import os
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from utils.logger import logger
import pytz


class GoogleCalendarService:
    """
    Servicio para obtener eventos de Google Calendar.
    Usa Service Account para autenticación (ideal para un solo usuario).
    """

    # Mapeo de categorías a colores de Google Calendar
    # Documentación: https://developers.google.com/calendar/api/v3/reference/colors
    COLOR_MAP = {
        "TRABAJO": "9",  # Azul (trabajo/productividad)
        "SALUD": "10",  # Verde (salud/bienestar)
        "OCIO": "11",  # Rojo (ocio/entretenimiento)
        "RUTINA": "5",  # Amarillo (rutinas diarias)
        "PERSONAL": "1",  # Lavanda (asuntos personales)
        "ESTUDIO": "7",  # Cyan (aprendizaje)
        "FAMILIA": "4",  # Flamingo (familia)
        "SOCIAL": "3",  # Púrpura (eventos sociales)
    }
    DEFAULT_COLOR = "8"  # Gris (sin categoría)

    def __init__(self):
        self.service_account_file = os.getenv(
            "GOOGLE_SERVICE_ACCOUNT_FILE", "credentials/service-account.json"
        )
        self.calendar_id = os.getenv("GOOGLE_CALENDAR_ID", "primary")
        self.timezone = os.getenv("TIMEZONE", "America/Lima")
        self.service = None
        self._initialize_service()

    def _initialize_service(self):
        """Inicializa el servicio de Google Calendar con credenciales."""
        try:
            if not os.path.exists(self.service_account_file):
                logger.error(f"\n❌ Google Calendar: Service account file not found")
                logger.error(f"   Expected: {self.service_account_file}")
                logger.error(f"\n💡 Solución:")
                logger.error(
                    f"   1. Descarga el archivo JSON de credenciales de Google Cloud"
                )
                logger.error(f"   2. Guárdalo en: {self.service_account_file}")
                logger.error(
                    f"   3. Verifica que GOOGLE_SERVICE_ACCOUNT_FILE en .env apunte al archivo correcto"
                )
                logger.error(
                    f"\n📚 Ver docs/GOOGLE_CALENDAR_INTEGRATION.md para instrucciones completas\n"
                )
                return

            creds = service_account.Credentials.from_service_account_file(
                self.service_account_file,
                scopes=["https://www.googleapis.com/auth/calendar"],  # Read & Write
            )
            self.service = build("calendar", "v3", credentials=creds)
            logger.info(f"✅ Google Calendar service initialized successfully")
            logger.info(f"   Calendar ID: {self.calendar_id}")
            logger.info(f"   Timezone: {self.timezone}")
        except FileNotFoundError:
            logger.error(
                f"\n❌ Google Calendar: Credentials file not found: {self.service_account_file}"
            )
            logger.error(f"📚 Ver docs/GOOGLE_CALENDAR_INTEGRATION.md para setup\n")
            self.service = None
        except json.JSONDecodeError:
            logger.error(f"\n❌ Google Calendar: Invalid JSON in credentials file")
            logger.error(f"   File: {self.service_account_file}")
            logger.error(
                f"💡 Verifica que el archivo JSON esté correctamente formateado\n"
            )
            self.service = None
        except Exception as e:
            logger.error(f"\n❌ Failed to initialize Google Calendar service")
            logger.error(f"   Error: {str(e)}")
            logger.error(f"💡 Posibles causas:")
            logger.error(f"   - Credenciales inválidas")
            logger.error(f"   - Service Account no tiene acceso al calendario")
            logger.error(f"   - API de Google Calendar no está habilitada")
            logger.error(
                f"\n📚 Ver docs/GOOGLE_CALENDAR_INTEGRATION.md para troubleshooting\n"
            )
            self.service = None

    def _get_timezone_aware_datetime(self, dt: datetime) -> datetime:
        """Convierte datetime a timezone aware si no lo es."""
        if dt.tzinfo is None:
            tz = pytz.timezone(self.timezone)
            return tz.localize(dt)
        return dt

    def get_events_in_range(
        self, start_time: datetime, end_time: datetime
    ) -> List[Dict]:
        """
        Obtiene eventos en un rango de tiempo específico.

        Args:
            start_time: Inicio del rango (datetime)
            end_time: Fin del rango (datetime)

        Returns:
            Lista de eventos en formato dict
        """
        if not self.service:
            logger.error("❌ Google Calendar service not initialized")
            return []

        try:
            # Asegurar que las fechas sean timezone aware
            start_time = self._get_timezone_aware_datetime(start_time)
            end_time = self._get_timezone_aware_datetime(end_time)

            # Convertir a formato ISO con timezone
            time_min = start_time.isoformat()
            time_max = end_time.isoformat()

            logger.info(f"📅 Fetching events from {time_min} to {time_max}")

            events_result = (
                self.service.events()
                .list(
                    calendarId=self.calendar_id,
                    timeMin=time_min,
                    timeMax=time_max,
                    singleEvents=True,
                    orderBy="startTime",
                    maxResults=100,
                )
                .execute()
            )

            events = events_result.get("items", [])
            logger.info(f"✅ Found {len(events)} events")
            return events

        except HttpError as e:
            logger.error(f"❌ Google Calendar API error: {e}")
            return []
        except Exception as e:
            logger.error(f"❌ Unexpected error fetching events: {e}")
            return []

    def get_today_events(self) -> List[Dict]:
        """Obtiene eventos del día actual."""
        tz = pytz.timezone(self.timezone)
        now = datetime.now(tz)
        start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = now.replace(hour=23, minute=59, second=59, microsecond=999999)

        return self.get_events_in_range(start_of_day, end_of_day)

    def get_week_events(self) -> List[Dict]:
        """Obtiene eventos de la semana actual (lunes a domingo)."""
        tz = pytz.timezone(self.timezone)
        now = datetime.now(tz)

        # Inicio de la semana (lunes)
        start_of_week = now - timedelta(days=now.weekday())
        start_of_week = start_of_week.replace(hour=0, minute=0, second=0, microsecond=0)

        # Fin de la semana (domingo)
        end_of_week = start_of_week + timedelta(
            days=6, hours=23, minutes=59, seconds=59
        )

        return self.get_events_in_range(start_of_week, end_of_week)

    def get_month_events(self) -> List[Dict]:
        """Obtiene eventos del mes actual."""
        tz = pytz.timezone(self.timezone)
        now = datetime.now(tz)

        # Primer día del mes
        start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        # Último día del mes
        if now.month == 12:
            end_of_month = now.replace(
                year=now.year + 1,
                month=1,
                day=1,
                hour=0,
                minute=0,
                second=0,
                microsecond=0,
            ) - timedelta(seconds=1)
        else:
            end_of_month = now.replace(
                month=now.month + 1, day=1, hour=0, minute=0, second=0, microsecond=0
            ) - timedelta(seconds=1)

        return self.get_events_in_range(start_of_month, end_of_month)

    def get_critical_events(self, days_ahead: int = 7) -> List[Dict]:
        """
        Obtiene eventos críticos (próximos N días).

        Args:
            days_ahead: Número de días hacia adelante a buscar (default: 7)

        Returns:
            Lista de eventos próximos
        """
        tz = pytz.timezone(self.timezone)
        now = datetime.now(tz)
        start_time = now
        end_time = now + timedelta(days=days_ahead)

        return self.get_events_in_range(start_time, end_time)

    def parse_event(self, event: Dict) -> Dict:
        """
        Parsea un evento de Google Calendar a formato mnemos.

        Args:
            event: Evento crudo de Google Calendar API

        Returns:
            Evento parseado con campos estandarizados
        """
        # Parsear fechas
        start = event.get("start", {})
        end = event.get("end", {})

        # Detectar si es evento de todo el día
        all_day = "date" in start

        if all_day:
            start_dt = datetime.fromisoformat(start["date"])
            end_dt = datetime.fromisoformat(end["date"])
        else:
            start_dt = datetime.fromisoformat(start.get("dateTime", ""))
            end_dt = datetime.fromisoformat(end.get("dateTime", ""))

        # Extraer metadata de la descripción (formato BUJO_META)
        description = event.get("description", "")
        extra_data = self._extract_metadata(description)

        return {
            "google_event_id": event["id"],
            "summary": event.get("summary", "Sin título"),
            "description": description,
            "location": event.get("location"),
            "start_datetime": start_dt,
            "end_datetime": end_dt,
            "all_day": all_day,
            "status": event.get("status", "confirmed"),
            "priority": extra_data.get("priority"),
            "category": extra_data.get("category"),
            "extra_data": extra_data,
        }

    def _extract_metadata(self, description: str) -> Dict:
        """
        Extrae metadata del formato BUJO_META de la descripción.

        Args:
            description: Descripción del evento

        Returns:
            Dict con metadata parseada
        """
        if not description:
            return {}

        import re

        match = re.search(r"BUJO_META:\s*(\{.*\})", description)
        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                logger.warning(f"⚠️  Failed to parse BUJO_META: {match.group(1)}")
                return {}
        return {}

    def _format_event_for_google(
        self, event_data: Dict, include_metadata: bool = True
    ) -> Dict:
        """
        Convierte evento de formato mnemos a formato Google Calendar.

        Args:
            event_data: Evento en formato interno
            include_metadata: Si incluir metadata en descripción

        Returns:
            Evento en formato Google Calendar API
        """
        google_event = {
            "summary": event_data.get("summary", "Sin título"),
            "location": event_data.get("location", ""),
            "status": event_data.get("status", "confirmed"),
        }

        # Mapear categoría a color de Google Calendar
        category = event_data.get("category")
        if category:
            google_event["colorId"] = self.COLOR_MAP.get(category, self.DEFAULT_COLOR)
        else:
            google_event["colorId"] = self.DEFAULT_COLOR

        # Descripción con metadata embebida
        description = event_data.get("description", "")
        if include_metadata:
            metadata = {
                "priority": event_data.get("priority"),
                "category": event_data.get("category"),
            }
            # Agregar metadata solo si hay valores
            metadata = {k: v for k, v in metadata.items() if v is not None}
            if metadata:
                description += f"\n\nBUJO_META: {json.dumps(metadata)}"

        google_event["description"] = description

        # Fechas
        all_day = event_data.get("all_day", False)
        start_dt = event_data["start_datetime"]
        end_dt = event_data["end_datetime"]

        if all_day:
            # Evento de todo el día (solo fecha)
            google_event["start"] = {"date": start_dt.strftime("%Y-%m-%d")}
            google_event["end"] = {"date": end_dt.strftime("%Y-%m-%d")}
        else:
            # Evento con hora específica
            google_event["start"] = {
                "dateTime": start_dt.isoformat(),
                "timeZone": self.timezone,
            }
            google_event["end"] = {
                "dateTime": end_dt.isoformat(),
                "timeZone": self.timezone,
            }

        return google_event

    # ==================== BIDIRECTIONAL SYNC METHODS ====================

    def create_event(self, event_data: Dict) -> Optional[Dict]:
        """
        Crea un evento en Google Calendar.

        Args:
            event_data: Datos del evento en formato interno

        Returns:
            Evento creado (formato Google) o None si falla
        """
        if not self.service:
            logger.error("❌ Google Calendar service not initialized")
            return None

        try:
            google_event = self._format_event_for_google(event_data)

            logger.info(
                f"📅 Creating event in Google Calendar: {event_data.get('summary')}"
            )

            created_event = (
                self.service.events()
                .insert(calendarId=self.calendar_id, body=google_event)
                .execute()
            )

            logger.info(
                f"✅ Event created in Google Calendar: {created_event.get('id')}"
            )
            return created_event

        except HttpError as e:
            logger.error(f"❌ Google Calendar API error creating event: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ Unexpected error creating event: {e}")
            return None

    def update_event(self, google_event_id: str, event_data: Dict) -> Optional[Dict]:
        """
        Actualiza un evento en Google Calendar.

        Args:
            google_event_id: ID del evento en Google Calendar
            event_data: Datos actualizados del evento

        Returns:
            Evento actualizado (formato Google) o None si falla
        """
        if not self.service:
            logger.error("❌ Google Calendar service not initialized")
            return None

        try:
            google_event = self._format_event_for_google(event_data)

            logger.info(f"📅 Updating event in Google Calendar: {google_event_id}")

            updated_event = (
                self.service.events()
                .update(
                    calendarId=self.calendar_id,
                    eventId=google_event_id,
                    body=google_event,
                )
                .execute()
            )

            logger.info(f"✅ Event updated in Google Calendar: {google_event_id}")
            return updated_event

        except HttpError as e:
            logger.error(f"❌ Google Calendar API error updating event: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ Unexpected error updating event: {e}")
            return None

    def delete_event(self, google_event_id: str) -> bool:
        """
        Elimina un evento de Google Calendar.

        Args:
            google_event_id: ID del evento en Google Calendar

        Returns:
            True si se eliminó correctamente, False si falla
        """
        if not self.service:
            logger.error("❌ Google Calendar service not initialized")
            return False

        try:
            logger.info(f"📅 Deleting event from Google Calendar: {google_event_id}")

            self.service.events().delete(
                calendarId=self.calendar_id, eventId=google_event_id
            ).execute()

            logger.info(f"✅ Event deleted from Google Calendar: {google_event_id}")
            return True

        except HttpError as e:
            if e.resp.status == 404:
                logger.warning(
                    f"⚠️  Event not found in Google Calendar: {google_event_id}"
                )
            else:
                logger.error(f"❌ Google Calendar API error deleting event: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Unexpected error deleting event: {e}")
            return False


# Singleton para reutilizar la instancia
_calendar_service = None


def get_calendar_service() -> GoogleCalendarService:
    """Obtiene instancia singleton del servicio de Google Calendar."""
    global _calendar_service
    if _calendar_service is None:
        _calendar_service = GoogleCalendarService()
    return _calendar_service
