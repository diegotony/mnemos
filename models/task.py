from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Date,DateTime
from database import Base

# Represents a task associated with a user. Can be marked as completed and has a due date.
class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, nullable=False)
    due_date = Column(DateTime(timezone=True),  nullable=True)
    is_completed = Column(Boolean, default=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    status_id = Column(Integer, ForeignKey("statuses.id"))
    priority_id = Column(Integer, ForeignKey("priorities.id"))
    time_bucket_id = Column(Integer, ForeignKey("time_buckets.id"))
