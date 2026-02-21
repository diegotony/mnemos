from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from models.priority import Priority
from schemas.priority import PriorityCreate, PriorityRead
from dependencies.database import get_db
from typing import List

router = APIRouter(prefix="/priorities", tags=["Priorities"])


@router.post("/", response_model=PriorityRead)
def create_priority(priority: PriorityCreate, db: Session = Depends(get_db)):
    db_priority = Priority(**priority.model_dump())
    db.add(db_priority)
    db.commit()
    db.refresh(db_priority)
    return db_priority


@router.get("/", response_model=List[PriorityRead])
def get_priorities(db: Session = Depends(get_db)):
    return db.query(Priority).all()
