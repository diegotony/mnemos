from sqlalchemy import Column, Integer, String, Date
from database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)         # Unique user ID
    name = Column(String, nullable=False)                      # Full name of the user
    birth_date = Column(Date, nullable=True)                   # Optional birth da_
    email = Column(String, unique=True, index=True)