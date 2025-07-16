from sqlalchemy import Column, Integer, String, Boolean, Date
from database import Base

# This model represents a personal habit that a user wants to track over time.
# It includes details like description, frequency, goal, and whether the habit is currently active.
class Habit(Base):
    __tablename__ = "habits"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)               # Name of the habit
    category = Column(String)                           # Category the habit belongs to (e.g., health, productivity)
    description = Column(String)                        # Optional description of the habit
    frequency = Column(String)                          # How often the habit should occur (e.g., daily, weekly)
    message = Column(String)                            # Optional motivational message or reminder
    color = Column(String)                              # Color associated with the habit (e.g., for UI)
    unit = Column(String)                               # Measurement unit (e.g., minutes, times)
    goal_value = Column(Integer)                        # Target value or amount for the habit
    is_active = Column(Boolean, default=True)           # Whether the habit is currently being tracked
    start_date = Column(Date)                           # When the habit tracking started
