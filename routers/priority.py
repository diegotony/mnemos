from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import SessionLocal
from models.priority import Priority
from schemas.priority import PriorityCreate, PriorityRead
from typing import List

router = APIRouter(prefix="/priorities", tags=["Priorities"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=PriorityRead)
def create_priority(priority: PriorityCreate, db: Session = Depends(get_db)):
    db_priority = Priority(**priority.dict())
    db.add(db_priority)
    db.commit()
    db.refresh(db_priority)
    return db_priority

@router.get("/", response_model=List[PriorityRead])
def get_priorities(db: Session = Depends(get_db)):
    return db.query(Priority).all()
