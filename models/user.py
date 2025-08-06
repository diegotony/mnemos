from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Date, DateTime
from database import Base
from sqlalchemy.sql import func


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)  # Unique user ID
    name = Column(String, nullable=False)  # Full name of the user
    birth_date = Column(Date, nullable=True)  # Optional birth da_
    email = Column(String, unique=True, index=True)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
