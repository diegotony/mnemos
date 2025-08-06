from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class TaskBase(BaseModel):
    user_id: int
    content: str
    due_date: Optional[datetime] = Field(None, example=None)
    completed_at: Optional[datetime] = Field(None, example=None)
    today: Optional[bool] = False
    priority_id: Optional[int] = None
    status_id: Optional[int] = None
    project_id: Optional[int] = None


class TaskCreate(TaskBase):
    pass  # no incluyes created_at


class TaskUpdate(BaseModel):
    content: Optional[str] = None
    due_date: Optional[datetime] = None
    today: Optional[bool] = None
    priority_id: Optional[int] = None
    status_id: Optional[int] = None
    project_id: Optional[int] = None
    completed_at: Optional[datetime] = None


class TaskRead(TaskBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
