from sqlalchemy import Column, Integer, String, Boolean, Date, ForeignKey, DateTime
from database import Base
from datetime import datetime, timezone
from utils.timezone import now_local

# Represents a daily log of a user's habit, including its value, completion status, and optional notes.
class HabitLog(Base):
    __tablename__ = "habit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)       # The user who owns the log
    habit_id = Column(Integer, ForeignKey("habits.id"), nullable=False)     # The habit being logged
    date = Column(DateTime(timezone=True), default=now_local)                              # Date of the log entry
    value = Column(Integer, nullable=True)                                  # Tracked value (e.g., minutes, count)
    completed = Column(Boolean, default=False)                              # Whether the habit was completed
    notes = Column(String, nullable=True)                                   # Optional notes or comments
