from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import SessionLocal
from models.habit_log import HabitLog
from schemas.habit_log import HabitLogCreate, HabitLogRead
import os
from dotenv import load_dotenv
from dependencies.user import get_current_user_id
from utils.logger import logger


load_dotenv()

router = APIRouter(prefix="/habit-logs", tags=["Habit Logs"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=HabitLogRead)
def create_habit_log(
    log: HabitLogCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    logger.debug("Creating Habit Log...")
    db_log = HabitLog(**log.dict(), user_id=user_id)
    logger.debug("Preparing Habit Log....")
    db.add(db_log)
    db.commit()
    logger.debug("Executed 'Creating Habit Log Transaction'...")
    logger.debug(f"Habit Log before commit: {db_log}")
    db.refresh(db_log)
    logger.debug("Updated db_log")
    logger.debug(f"Habit Log after refresh: {db_log}")
    return db_log


@router.get("/", response_model=List[HabitLogRead])
def get_all_habit_logs(db: Session = Depends(get_db)):
    return db.query(HabitLog).all()
