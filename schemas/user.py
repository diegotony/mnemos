from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import date

class UserBase(BaseModel):
    name: str
    email: EmailStr
    birth_date: Optional[str] = None  # Puede usar datetime.date si preferís

class UserCreate(UserBase):
    pass

class UserRead(UserBase):
    id: int
    birth_date: Optional[date] = None  # permite nulo
    
    class Config:
        from_attributes = True
