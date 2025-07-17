from pydantic import BaseModel
from typing import Optional
from datetime import date

class HabitBase(BaseModel):
    name: str
    category: Optional[str] = None
    description: Optional[str] = None
    frequency: Optional[str] = None
    message: Optional[str] = None
    color: Optional[str] = None
    unit: Optional[str] = None
    goal_value: Optional[int] = None
    is_active: Optional[bool] = True
    start_date: Optional[date] = None

class HabitCreate(HabitBase):
    pass

class HabitRead(HabitBase):
    id: int
    start_date: Optional[date] = None  # permite nulo

    class Config:
        from_attributes = True
