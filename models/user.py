from sqlalchemy import Column, Integer, String, Date
from database import Base

# This model represents a user of the system.
# It stores basic personal information such as name, birth date, and email.
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)         # Unique user ID
    name = Column(String, nullable=False)                      # Full name of the user
    birth_date = Column(Date, nullable=True)                   # Optional birth da_
    email = Column(String, unique=True, index=True)