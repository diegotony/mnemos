from sqlalchemy import Column, Integer, String
from database import Base

# Represents a planning bucket like "Today", "This week", etc.
class TimeBucket(Base):
    __tablename__ = "time_buckets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)      # Ej: "Hoy", "Mañana"
    slug = Column(String, nullable=False, unique=True)      # Ej: "today", "tomorrow"
