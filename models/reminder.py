
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from database import Base
from utils.timezone import now_local

# Represents a scheduled reminder, which can be linked to a user, task, or habit.
class Reminder(Base):
    __tablename__ = "reminders"

    id = Column(Integer, primary_key=True, index=True)
    message = Column(String, nullable=False)                     # Reminder message text
    scheduled_time =Column(DateTime(timezone=True), default=now_local)           # When the reminder should trigger
    is_active = Column(Boolean, default=True)                    # Whether the reminder is currently active
    user_id = Column(Integer, ForeignKey("users.id"))            # Owner of the reminder
