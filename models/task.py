from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Date,DateTime
from database import Base
from utils.timezone import now_local
# Represents a task associated with a user. Can be marked as completed and has a due date.
class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String)
    due_date = Column(DateTime(timezone=True), default=now_local)
    is_completed = Column(Boolean, default=False)
    user_id = Column(Integer, ForeignKey("users.id"))
