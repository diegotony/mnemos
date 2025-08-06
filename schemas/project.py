from pydantic import BaseModel, EmailStr
from datetime import date
from typing import Optional


class ProjectBase(BaseModel):
    name: str
    content: str
    user_id: int
    area_id:  Optional[int] = None


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    content: Optional[str] = None
    email: Optional[EmailStr] = None
    user_id: Optional[int] = None
    area_id:  Optional[int] = None
    


class ProjectRead(ProjectBase):
    id: int

    class Config:
        from_attributes = True
