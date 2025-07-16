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

class TaskRead(TaskBase):
    id: int

    class Config:
        orm_mode = True
