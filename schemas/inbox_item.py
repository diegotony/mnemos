# schemas/inbox_item.py

from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from models.inbox_item import SourceType


class InboxItemBase(BaseModel):
    user_id: Optional[int] = None
    content: str
    status_id: Optional[int] = 5
    source: SourceType


class InboxItemCreate(InboxItemBase):
    pass


class InboxItemUpdate(BaseModel):
    content: Optional[str] = None
    status_id: Optional[int] = None
    source: Optional[SourceType] = None


class InboxItemRead(InboxItemBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True
