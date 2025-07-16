from pydantic import BaseModel
from typing import Optional
from datetime import date

class IdeaBase(BaseModel):
    title: str
    description: Optional[str] = None
    created_date: Optional[date] = None
    user_id: int
    category_id: Optional[int] = None
    priority_id: Optional[int] = None

class IdeaCreate(IdeaBase):
    pass

class IdeaRead(IdeaBase):
    id: int

    class Config:
        from_attributes = True
