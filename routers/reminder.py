from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import SessionLocal
from models.reminder import Reminder
from schemas.reminder import ReminderCreate, ReminderRead
from typing import List

router = APIRouter(prefix="/reminders", tags=["Reminders"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=ReminderRead)
def create_reminder(reminder: ReminderCreate, db: Session = Depends(get_db)):
    db_reminder = Reminder(**reminder.dict())
    db.add(db_reminder)
    db.commit()
    db.refresh(db_reminder)
    return db_reminder

@router.get("/", response_model=List[ReminderRead])
def get_reminders(db: Session = Depends(get_db)):
    return db.query(Reminder).all()
