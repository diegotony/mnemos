from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import SessionLocal
from models.habit_log import HabitLog
from schemas.habit_log import HabitLogCreate, HabitLogRead

router = APIRouter(prefix="/habit-logs", tags=["Habit Logs"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=HabitLogRead)
def create_habit_log(log: HabitLogCreate, db: Session = Depends(get_db)):
    db_log = HabitLog(**log.dict())
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log

@router.get("/", response_model=List[HabitLogRead])
def get_all_habit_logs(db: Session = Depends(get_db)):
    return db.query(HabitLog).all()
