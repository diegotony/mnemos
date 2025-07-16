from pydantic import BaseModel
from typing import Optional
from datetime import date

class ReflectionBase(BaseModel):
    text: Optional[str] = None
    date: date
    user_id: int

class ReflectionCreate(ReflectionBase):
    pass

class ReflectionRead(ReflectionBase):
    id: int

    class Config:
        from_attributes = True
