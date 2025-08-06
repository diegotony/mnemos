from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class IdeaBase(BaseModel):
    content: str
    user_id: Optional[int] = None

class IdeaCreate(IdeaBase):
    pass

class IdeaUpdate(BaseModel):
    content: Optional[str] = None
    user_id: Optional[int] = None

class IdeaRead(IdeaBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True
