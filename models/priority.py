from sqlalchemy import Column, Integer, String
from database import Base

# Represents the priority level of a task or habit (e.g., low, medium, high)
class Priority(Base):
    __tablename__ = "priorities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
