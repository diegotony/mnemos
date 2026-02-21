from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict, Any


class CalendarEventBase(BaseModel):
    summary: str
    description: Optional[str] = None
    location: Optional[str] = None
    start_datetime: datetime
    end_datetime: datetime
    all_day: bool = False
    status: Optional[str] = None
    priority: Optional[str] = None
    category: Optional[str] = None
    extra_data: Optional[Dict[str, Any]] = None


class CalendarEventCreate(CalendarEventBase):
    google_event_id: str
    user_id: Optional[int] = None


class CalendarEventUpdate(BaseModel):
    summary: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    start_datetime: Optional[datetime] = None
    end_datetime: Optional[datetime] = None
    all_day: Optional[bool] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    category: Optional[str] = None
    extra_data: Optional[Dict[str, Any]] = None


class CalendarEventRead(CalendarEventBase):
    id: int
    google_event_id: str
    user_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    synced_at: datetime

    class Config:
        from_attributes = True


class CalendarEventSummary(BaseModel):
    """Schema simplificado para listados rápidos"""

    id: int
    google_event_id: str
    summary: str
    start_datetime: datetime
    end_datetime: datetime
    all_day: bool
    priority: Optional[str] = None
    category: Optional[str] = None

    class Config:
        from_attributes = True
