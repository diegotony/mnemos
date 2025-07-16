from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from database import Base
from utils.timezone import now_local
# Represents a motivational or inspirational phrase. Can be global or user-created.
class Phrase(Base):
    __tablename__ = "phrases"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, nullable=False)
    is_custom = Column(Boolean, default=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), default=now_local)