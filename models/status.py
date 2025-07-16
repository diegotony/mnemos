from sqlalchemy import Column, Integer, String
from database import Base

# Represents a general status entity, which can be used to tag or describe various items.
class Status(Base):
    __tablename__ = "statuses"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
