from pydantic import BaseModel
from typing import Optional
from datetime import date

class TaskBase(BaseModel):
    text: str
    due_date: Optional[date] = None
    is_completed: Optional[bool] = False
    user_id: int
    status_id: int
    priority_id: int
    time_bucket_id: int

class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    text: Optional[str] = None
    due_date: Optional[date] = None
    status_id: Optional[int] = None
    priority_id: Optional[int] = None
    user_id: Optional[int] = None

class TaskRead(TaskBase):
    id: int

    class Config:
        from_attributes = True
