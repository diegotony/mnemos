from sqlalchemy import Column, Integer, String, Text, Date, ForeignKey
from database import Base
from datetime import date

# Represents a user-created idea, which can be categorized and prioritized
class Idea(Base):
    __tablename__ = "ideas"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, nullable=False)                          # Short title of the idea
    created_date = Column(Date, default=date.today)                # Date the idea was registered
    user_id = Column(Integer, ForeignKey("users.id"))              # Author/owner of the idea
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)  # Optional category

