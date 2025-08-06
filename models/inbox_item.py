from enum import Enum
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum as SQLEnum
from sqlalchemy.sql import func
from database import Base

class SourceType(str, Enum):
    manual  = "manual"
    cli     = "cli"
    web     = "web"
    discord = "discord"



class InboxItem(Base):
    __tablename__ = "inbox"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    content = Column(String, nullable=False)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    status_id = Column(Integer, ForeignKey("statuses.id"), default=5)
    source     = Column(
        SQLEnum(SourceType, name="source_type", native_enum=True),
        nullable=False,
        default=SourceType.manual        # ahora es una cadena (SourceType es subclass de str)
    )