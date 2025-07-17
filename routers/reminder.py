from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import SessionLocal
from models.reminder import Reminder
from schemas.reminder import ReminderCreate, ReminderRead
from typing import List
from utils.logger import logger
from dependencies.user import get_current_user_id

router = APIRouter(prefix="/reminders", tags=["Reminders"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=ReminderRead)
def create_reminder(
    reminder: ReminderCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    logger.debug("Creating Reminder...")
    db_reminder = Reminder(**reminder.dict(), user_id=user_id)
    logger.debug("Preparing Creating Reminder...")
    db.add(db_reminder)
    db.commit()
    logger.debug("Executed 'Creating Reminder Transaction'...")
    logger.debug(f"Reminder before commit: {db_reminder}")
    db.refresh(db_reminder)
    logger.debug("Updated db_reminder")
    logger.debug(f"Reminder after refresh: {db_reminder}")
    return db_reminder


@router.get("/", response_model=List[ReminderRead])
def get_reminders(db: Session = Depends(get_db)):
    return db.query(Reminder).all()
