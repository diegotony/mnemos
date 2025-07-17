from pydantic import BaseModel
from typing import Optional
from datetime import date

class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    due_date: Optional[date] = None
    is_completed: Optional[bool] = False
    user_id: int

class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    due_date: Optional[date] = None
    status_id: Optional[int] = None
    priority_id: Optional[int] = None
    habit_id: Optional[int] = None
    reminder_id: Optional[int] = None
    user_id: Optional[int] = None

class TaskRead(TaskBase):
    id: int

    class Config:
        from_attributes = True
