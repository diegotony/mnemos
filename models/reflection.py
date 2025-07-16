from sqlalchemy import Column, Integer, String, Date, ForeignKey,DateTime
from database import Base
from utils.timezone import now_local

# Represents a personal reflection associated with a user and a specific date.
class Reflection(Base):
    __tablename__ = "reflections"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String)
    date = Column(Date)
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), default=now_local)