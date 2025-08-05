from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Date, DateTime
from database import Base

# Represents a task associated with a user. Can be marked as completed and has a due date.
class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    # User asociated to task
    user_id = Column(Integer, ForeignKey("users.id"))
    
    # Base task
    content = Column(String, nullable=False)
    due_date = Column(DateTime(timezone=True), nullable=True)
    today = Column(Boolean, nullable=True, default=False)
    priority_id = Column(Integer, ForeignKey("priorities.id"))
    status_id = Column(Integer, ForeignKey("statuses.id"))

    # #* Recurrence task 
    # recurrence_type = Column(String, nullable=True)
    # recurrence_interval = Column(Integer, nullable=True)
    # recurrence_end_date = Column(DateTime(timezone=True), nullable=True)
    
    # last_generated_date = Column(DateTime(timezone=True), nullable=True)
    # recurrence_weekday = Column(Integer, nullable=True)
    # recurrence_month_day = Column(Integer, nullable=True)
    # recurrence_week_of_month = Column(Integer, nullable=True)
    
    # If the task is asociated to Project
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)

    # When was completed
    completed_at = Column(DateTime(timezone=True), nullable=True)
    