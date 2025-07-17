from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ReminderBase(BaseModel):
    message: str
    scheduled_time: datetime
    is_active: Optional[bool] = True
    user_id: int

class ReminderCreate(ReminderBase):
    pass

class ReminderRead(ReminderBase):
    id: int
    scheduled_time: Optional[datetime] = None  # permite nulo

    class Config:
        from_attributes = True
