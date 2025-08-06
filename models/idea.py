from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Date, DateTime
from database import Base
from sqlalchemy.sql import func


class Idea(Base):
    __tablename__ = "ideas"
    id = Column(Integer, primary_key=True, index=True)
    content = Column(String, nullable=False)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
