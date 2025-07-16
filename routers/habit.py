from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import SessionLocal
from models.habit import Habit
from schemas.habit import HabitCreate, HabitRead
from typing import List

router = APIRouter(prefix="/habits", tags=["Habits"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=HabitRead)
def create_habit(habit: HabitCreate, db: Session = Depends(get_db)):
    db_habit = Habit(**habit.dict())
    db.add(db_habit)
    db.commit()
    db.refresh(db_habit)
    return db_habit

@router.get("/", response_model=List[HabitRead])
def get_habits(db: Session = Depends(get_db)):
    return db.query(Habit).all()
