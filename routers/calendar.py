"""
Router para endpoints de Google Calendar.
Proporciona acceso a eventos del calendario con diferentes filtros.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from models.calendar_event import CalendarEvent
from schemas.calendar_event import (
    CalendarEventRead,
    CalendarEventSummary,
    CalendarEventCreate,
    CalendarEventUpdate,
)
from dependencies.database import get_db
from services.google_calendar import get_calendar_service
from utils.logger import logger


router = APIRouter(prefix="/calendar", tags=["Calendar"])


@router.get("/categories")
def get_categories():
    """
    Lista todas las categorías disponibles con sus colores de Google Calendar.

    Retorna un diccionario con:
    - Nombre de categoría
    - ID de color en Google Calendar
    - Descripción del color
    """
    calendar_service = get_calendar_service()

    # Mapeo de colorId a nombre de color (para referencia)
    color_names = {
        "1": "Lavanda",
        "2": "Salvia",
        "3": "Uva",
        "4": "Flamingo",
        "5": "Banana",
        "6": "Mandarina",
        "7": "Pavo real",
        "8": "Grafito",
        "9": "Arándano",
        "10": "Albahaca",
        "11": "Tomate",
    }

    categories = {}
    for category, color_id in calendar_service.COLOR_MAP.items():
        categories[category] = {
            "color_id": color_id,
            "color_name": color_names.get(color_id, "Desconocido"),
        }

    # Agregar la categoría por defecto
    categories["SIN_CATEGORIA"] = {
        "color_id": calendar_service.DEFAULT_COLOR,
        "color_name": color_names.get(calendar_service.DEFAULT_COLOR, "Desconocido"),
    }

    return categories


@router.get("/sync/today", response_model=List[CalendarEventSummary])
def sync_today_events(db: Session = Depends(get_db)):
    """
    Sincroniza y obtiene eventos del día actual desde Google Calendar.
    """
    calendar_service = get_calendar_service()

    # Validar que el servicio esté inicializado
    if not calendar_service.service:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Google Calendar service not configured. Please check your credentials and configuration.",
        )

    try:
        # Obtener eventos de Google Calendar
        google_events = calendar_service.get_today_events()
        logger.info(f"📅 Syncing {len(google_events)} events from today")

        synced_events = []
        for google_event in google_events:
            parsed_event = calendar_service.parse_event(google_event)

            # Verificar si ya existe en la BD
            existing = (
                db.query(CalendarEvent)
                .filter(
                    CalendarEvent.google_event_id == parsed_event["google_event_id"]
                )
                .first()
            )

            if existing:
                # Actualizar evento existente
                for key, value in parsed_event.items():
                    if key != "google_event_id":
                        setattr(existing, key, value)
                db_event = existing
            else:
                # Crear nuevo evento
                db_event = CalendarEvent(**parsed_event)
                db.add(db_event)

            synced_events.append(db_event)

        db.commit()
        logger.info(f"✅ Successfully synced {len(synced_events)} events")
        return synced_events

    except Exception as e:
        logger.error(f"❌ Error syncing today events: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to sync events: {str(e)}",
        )


@router.get("/sync/week", response_model=List[CalendarEventSummary])
def sync_week_events(db: Session = Depends(get_db)):
    """
    Sincroniza y obtiene eventos de la semana actual desde Google Calendar.
    """
    calendar_service = get_calendar_service()

    # Validar que el servicio esté inicializado
    if not calendar_service.service:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Google Calendar service not configured. Please check your credentials and configuration.",
        )

    try:
        google_events = calendar_service.get_week_events()
        logger.info(f"📅 Syncing {len(google_events)} events from this week")

        synced_events = []
        for google_event in google_events:
            parsed_event = calendar_service.parse_event(google_event)

            existing = (
                db.query(CalendarEvent)
                .filter(
                    CalendarEvent.google_event_id == parsed_event["google_event_id"]
                )
                .first()
            )

            if existing:
                for key, value in parsed_event.items():
                    if key != "google_event_id":
                        setattr(existing, key, value)
                # synced_at se actualiza automáticamente
                db_event = existing
            else:
                db_event = CalendarEvent(**parsed_event)
                db.add(db_event)

            synced_events.append(db_event)

        db.commit()
        logger.info(f"✅ Successfully synced {len(synced_events)} events")
        return synced_events

    except Exception as e:
        logger.error(f"❌ Error syncing week events: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to sync events: {str(e)}",
        )


@router.get("/sync/month", response_model=List[CalendarEventSummary])
def sync_month_events(db: Session = Depends(get_db)):
    """
    Sincroniza y obtiene eventos del mes actual desde Google Calendar.
    """
    calendar_service = get_calendar_service()

    # Validar que el servicio esté inicializado
    if not calendar_service.service:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Google Calendar service not configured. Please check your credentials and configuration.",
        )

    try:
        google_events = calendar_service.get_month_events()
        logger.info(f"📅 Syncing {len(google_events)} events from this month")

        synced_events = []
        for google_event in google_events:
            parsed_event = calendar_service.parse_event(google_event)

            existing = (
                db.query(CalendarEvent)
                .filter(
                    CalendarEvent.google_event_id == parsed_event["google_event_id"]
                )
                .first()
            )

            if existing:
                for key, value in parsed_event.items():
                    if key != "google_event_id":
                        setattr(existing, key, value)
                # synced_at se actualiza automáticamente
                db_event = existing
            else:
                db_event = CalendarEvent(**parsed_event)
                db.add(db_event)

            synced_events.append(db_event)

        db.commit()
        logger.info(f"✅ Successfully synced {len(synced_events)} events")
        return synced_events

    except Exception as e:
        logger.error(f"❌ Error syncing month events: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to sync events: {str(e)}",
        )


@router.get("/sync/critical", response_model=List[CalendarEventSummary])
def sync_critical_events(
    days_ahead: int = Query(7, ge=1, le=30, description="Días hacia adelante"),
    db: Session = Depends(get_db),
):
    """
    Sincroniza y obtiene eventos críticos (próximos N días) desde Google Calendar.

    - **days_ahead**: Número de días hacia adelante (default: 7, max: 30)
    """
    calendar_service = get_calendar_service()

    # Validar que el servicio esté inicializado
    if not calendar_service.service:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Google Calendar service not configured. Please check your credentials and configuration.",
        )

    try:
        google_events = calendar_service.get_critical_events(days_ahead=days_ahead)
        logger.info(
            f"📅 Syncing {len(google_events)} critical events (next {days_ahead} days)"
        )

        synced_events = []
        for google_event in google_events:
            parsed_event = calendar_service.parse_event(google_event)

            existing = (
                db.query(CalendarEvent)
                .filter(
                    CalendarEvent.google_event_id == parsed_event["google_event_id"]
                )
                .first()
            )

            if existing:
                for key, value in parsed_event.items():
                    if key != "google_event_id":
                        setattr(existing, key, value)
                # synced_at se actualiza automáticamente
                db_event = existing
            else:
                db_event = CalendarEvent(**parsed_event)
                db.add(db_event)

            synced_events.append(db_event)

        db.commit()
        logger.info(f"✅ Successfully synced {len(synced_events)} critical events")
        return synced_events

    except Exception as e:
        logger.error(f"❌ Error syncing critical events: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to sync events: {str(e)}",
        )


@router.get("/events", response_model=List[CalendarEventRead])
def list_cached_events(
    skip: int = 0,
    limit: int = 100,
    category: Optional[str] = None,
    priority: Optional[str] = None,
    search: Optional[str] = Query(None, description="Buscar en título y descripción"),
    start_date: Optional[datetime] = Query(None, description="Fecha de inicio (desde)"),
    end_date: Optional[datetime] = Query(None, description="Fecha de fin (hasta)"),
    db: Session = Depends(get_db),
):
    """
    Lista eventos cacheados localmente con filtros opcionales.

    - **skip**: Número de registros a saltar (default: 0)
    - **limit**: Número máximo de registros (default: 100)
    - **category**: Filtrar por categoría (TRABAJO, SALUD, OCIO, RUTINA)
    - **priority**: Filtrar por prioridad (low, medium, high, critical)
    - **search**: Buscar texto en título y descripción (case-insensitive)
    - **start_date**: Mostrar eventos desde esta fecha (ISO format: 2026-02-20T00:00:00)
    - **end_date**: Mostrar eventos hasta esta fecha (ISO format: 2026-02-28T23:59:59)
    """
    query = db.query(CalendarEvent)

    if category:
        query = query.filter(CalendarEvent.category == category)
    if priority:
        query = query.filter(CalendarEvent.priority == priority)

    # Búsqueda por texto en título y descripción
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            (CalendarEvent.summary.ilike(search_pattern))
            | (CalendarEvent.description.ilike(search_pattern))
        )

    # Filtro por rango de fechas
    if start_date:
        query = query.filter(CalendarEvent.start_datetime >= start_date)
    if end_date:
        query = query.filter(CalendarEvent.end_datetime <= end_date)

    events = (
        query.order_by(CalendarEvent.start_datetime).offset(skip).limit(limit).all()
    )
    return events


@router.get("/events/{event_id}", response_model=CalendarEventRead)
def get_event(event_id: int, db: Session = Depends(get_db)):
    """Obtiene un evento específico por ID."""
    event = db.query(CalendarEvent).filter(CalendarEvent.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event


@router.post(
    "/events", response_model=CalendarEventRead, status_code=status.HTTP_201_CREATED
)
def create_event(event_data: CalendarEventCreate, db: Session = Depends(get_db)):
    """
    Crea un nuevo evento local.

    Este evento se guarda solo en la base de datos local.
    Para sincronizarlo con Google Calendar, usa los endpoints de sync.

    - **google_event_id**: ID único del evento (genera uno si es evento local)
    - **summary**: Título del evento (requerido)
    - **start_datetime**: Fecha/hora de inicio (requerido)
    - **end_datetime**: Fecha/hora de fin (requerido)
    - **category**: TRABAJO, SALUD, OCIO, RUTINA
    - **priority**: low, medium, high, critical
    """
    try:
        # Verificar que el google_event_id sea único
        existing = (
            db.query(CalendarEvent)
            .filter(CalendarEvent.google_event_id == event_data.google_event_id)
            .first()
        )

        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Event with google_event_id '{event_data.google_event_id}' already exists",
            )

        # Validar que end_datetime sea posterior a start_datetime
        if event_data.end_datetime <= event_data.start_datetime:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="end_datetime must be after start_datetime",
            )

        # Crear evento
        db_event = CalendarEvent(**event_data.model_dump())
        db.add(db_event)
        db.commit()
        db.refresh(db_event)

        logger.info(f"✅ Created event: {db_event.summary} (ID: {db_event.id})")
        return db_event

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Error creating event: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create event: {str(e)}",
        )


@router.put("/events/{event_id}", response_model=CalendarEventRead)
def update_event(
    event_id: int, event_data: CalendarEventUpdate, db: Session = Depends(get_db)
):
    """
    Actualiza un evento existente (actualización completa).

    Solo actualiza los campos proporcionados, los demás se mantienen igual.

    - **summary**: Nuevo título
    - **description**: Nueva descripción
    - **start_datetime**: Nueva fecha/hora de inicio
    - **end_datetime**: Nueva fecha/hora de fin
    - **category**: Nueva categoría
    - **priority**: Nueva prioridad
    """
    try:
        # Buscar evento
        event = db.query(CalendarEvent).filter(CalendarEvent.id == event_id).first()
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")

        # Validar fechas si se proporcionan ambas
        if (
            event_data.start_datetime is not None
            and event_data.end_datetime is not None
        ):
            if event_data.end_datetime <= event_data.start_datetime:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="end_datetime must be after start_datetime",
                )
        elif event_data.end_datetime is not None:
            # Solo se actualiza end_datetime, validar con start existente
            # Convertir a datetime para comparación
            current_start: datetime = event.start_datetime  # type: ignore
            if event_data.end_datetime <= current_start:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="end_datetime must be after start_datetime",
                )
        elif event_data.start_datetime is not None:
            # Solo se actualiza start_datetime, validar con end existente
            # Convertir a datetime para comparación
            current_end: datetime = event.end_datetime  # type: ignore
            if current_end <= event_data.start_datetime:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="end_datetime must be after start_datetime",
                )

        # Actualizar campos proporcionados
        update_data = event_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(event, field, value)

        # updated_at se actualiza automáticamente con onupdate

        db.commit()
        db.refresh(event)

        logger.info(f"✅ Updated event: {event.summary} (ID: {event.id})")
        return event

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Error updating event {event_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update event: {str(e)}",
        )


@router.patch("/events/{event_id}", response_model=CalendarEventRead)
def patch_event(
    event_id: int, event_data: CalendarEventUpdate, db: Session = Depends(get_db)
):
    """
    Actualiza parcialmente un evento (PATCH).

    Similar a PUT pero semánticamente indica actualización parcial.
    Solo los campos enviados serán actualizados.

    - **summary**: Actualizar título
    - **category**: Actualizar categoría
    - **priority**: Actualizar prioridad
    """
    # Reutilizar lógica de PUT
    return update_event(event_id, event_data, db)


@router.delete("/events/{event_id}")
def delete_cached_event(event_id: int, db: Session = Depends(get_db)):
    """
    Elimina un evento del caché local (NO lo elimina de Google Calendar).

    Para eliminar también de Google Calendar, usa DELETE /events/{id}/sync
    """
    event = db.query(CalendarEvent).filter(CalendarEvent.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    db.delete(event)
    db.commit()
    return {"message": f"Event {event_id} deleted from cache"}


# ==================== BIDIRECTIONAL SYNC ENDPOINTS ====================


@router.post("/events/{event_id}/push", response_model=CalendarEventRead)
def push_event_to_google(event_id: int, db: Session = Depends(get_db)):
    """
    Crea o actualiza un evento en Google Calendar basado en el evento local.

    - Si el evento no existe en Google Calendar: lo **crea**
    - Si ya existe: lo **actualiza**

    Actualiza el google_event_id en la base de datos local.
    """
    calendar_service = get_calendar_service()

    # Validar que el servicio esté inicializado
    if not calendar_service.service:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Google Calendar service not configured. Please check your credentials and configuration.",
        )

    try:
        # Buscar evento local
        event = db.query(CalendarEvent).filter(CalendarEvent.id == event_id).first()
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")

        # Convertir a dict para enviar a Google
        event_data = {
            "summary": event.summary,
            "description": event.description or "",
            "location": event.location,
            "start_datetime": event.start_datetime,
            "end_datetime": event.end_datetime,
            "all_day": event.all_day,
            "status": event.status or "confirmed",
            "priority": event.priority,
            "category": event.category,
        }

        # Verificar si ya existe en Google Calendar
        google_event_id_str: str = event.google_event_id  # type: ignore
        if google_event_id_str and google_event_id_str.startswith("local_"):
            # Es un evento local, crear en Google
            google_event = calendar_service.create_event(event_data)
            if not google_event:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to create event in Google Calendar",
                )

            # Actualizar google_event_id
            event.google_event_id = google_event["id"]
            logger.info(f"✅ Created event in Google Calendar: {google_event['id']}")

        else:
            # Ya existe en Google, actualizar
            google_event = calendar_service.update_event(
                google_event_id_str, event_data
            )
            if not google_event:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to update event in Google Calendar",
                )
            logger.info(f"✅ Updated event in Google Calendar: {event.google_event_id}")

        db.commit()
        db.refresh(event)
        return event

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Error pushing event to Google Calendar: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to push event to Google Calendar: {str(e)}",
        )


@router.delete("/events/{event_id}/sync")
def delete_event_from_google(event_id: int, db: Session = Depends(get_db)):
    """
    Elimina un evento tanto de la base de datos local como de Google Calendar.

    - Elimina de Google Calendar (si existe)
    - Elimina de la base de datos local
    """
    calendar_service = get_calendar_service()

    # Validar que el servicio esté inicializado
    if not calendar_service.service:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Google Calendar service not configured. Please check your credentials and configuration.",
        )

    try:
        # Buscar evento local
        event = db.query(CalendarEvent).filter(CalendarEvent.id == event_id).first()
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")

        # Intentar eliminar de Google Calendar (si no es local)
        google_event_id_str: str = event.google_event_id  # type: ignore
        if google_event_id_str and not google_event_id_str.startswith("local_"):
            success = calendar_service.delete_event(google_event_id_str)
            if not success:
                logger.warning(
                    f"⚠️  Failed to delete from Google Calendar, but will delete from local DB"
                )

        # Eliminar de la base de datos local
        db.delete(event)
        db.commit()

        return {
            "message": f"Event {event_id} deleted from both local database and Google Calendar",
            "google_event_id": google_event_id_str,
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Error deleting event: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete event: {str(e)}",
        )


@router.get("/health")
def check_calendar_health():
    """
    Verifica el estado de la configuración de Google Calendar.

    Returns:
        - configured: Si el servicio está configurado correctamente
        - calendar_id: ID del calendario configurado
        - timezone: Timezone configurado
        - message: Mensaje descriptivo del estado
    """
    import os

    calendar_service = get_calendar_service()
    service_account_file = os.getenv(
        "GOOGLE_SERVICE_ACCOUNT_FILE", "credentials/service-account.json"
    )

    # Verificar archivo de credenciales
    credentials_exist = os.path.exists(service_account_file)

    if not credentials_exist:
        return {
            "configured": False,
            "calendar_id": calendar_service.calendar_id,
            "timezone": calendar_service.timezone,
            "credentials_file": service_account_file,
            "credentials_exist": False,
            "service_initialized": False,
            "message": f"❌ Service account file not found: {service_account_file}. Please add your Google Calendar credentials.",
            "help": "See docs/GOOGLE_CALENDAR_INTEGRATION.md for setup instructions",
        }

    if not calendar_service.service:
        return {
            "configured": False,
            "calendar_id": calendar_service.calendar_id,
            "timezone": calendar_service.timezone,
            "credentials_file": service_account_file,
            "credentials_exist": True,
            "service_initialized": False,
            "message": "❌ Google Calendar service failed to initialize. Check credentials and API access.",
            "help": "See docs/GOOGLE_CALENDAR_INTEGRATION.md for troubleshooting",
        }

    return {
        "configured": True,
        "calendar_id": calendar_service.calendar_id,
        "timezone": calendar_service.timezone,
        "credentials_file": service_account_file,
        "credentials_exist": True,
        "service_initialized": True,
        "message": "✅ Google Calendar service is properly configured and ready to use",
    }
