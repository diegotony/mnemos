from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class AreaBase(BaseModel):
    name: str
    content: str
    user_id: Optional[int] = None

class AreaCreate(AreaBase):
    pass

class AreaUpdate(BaseModel):
    name: Optional[str] = None
    content: Optional[str] = None
    user_id: Optional[int] = None

class AreaRead(AreaBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
