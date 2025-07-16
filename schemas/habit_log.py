from pydantic import BaseModel
from typing import Optional
from datetime import date

class HabitLogBase(BaseModel):
    user_id: int
    habit_id: int
    date: date
    value: Optional[int] = None
    completed: Optional[bool] = False
    notes: Optional[str] = None

class HabitLogCreate(HabitLogBase):
    pass

class HabitLogRead(HabitLogBase):
    id: int

    class Config:
        orm_mode = True
