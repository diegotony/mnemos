from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    ForeignKey,
    DateTime,
    Text,
    JSON,
)
from database import Base
from sqlalchemy.sql import func


class CalendarEvent(Base):
    """
    Modelo para cachear eventos de Google Calendar localmente.
    Permite consultas rápidas sin llamar a la API cada vez.
    """

    __tablename__ = "calendar_events"

    id = Column(Integer, primary_key=True, index=True)
    google_event_id = Column(String, unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Información del evento
    summary = Column(String, nullable=False)  # Título del evento
    description = Column(Text, nullable=True)  # Descripción completa
    location = Column(String, nullable=True)

    # Fechas y horarios
    start_datetime = Column(DateTime(timezone=True), nullable=False, index=True)
    end_datetime = Column(DateTime(timezone=True), nullable=False)
    all_day = Column(Boolean, default=False)

    # Metadata del evento
    status = Column(String, nullable=True)  # confirmed, tentative, cancelled
    priority = Column(String, nullable=True, index=True)  # low, medium, high, critical
    category = Column(String, nullable=True, index=True)  # TRABAJO, SALUD, OCIO, RUTINA

    # Metadata adicional (almacenada como JSON)
    # Nota: No usar 'metadata' porque es reservado en SQLAlchemy
    extra_data = Column(JSON, nullable=True)

    # Timestamps
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    synced_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
