from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import SessionLocal
from models.status import Status
from schemas.status import StatusCreate, StatusRead
from typing import List

router = APIRouter(prefix="/statuses", tags=["Statuses"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=StatusRead)
def create_status(status: StatusCreate, db: Session = Depends(get_db)):
    db_status = Status(**status.dict())
    db.add(db_status)
    db.commit()
    db.refresh(db_status)
    return db_status

@router.get("/", response_model=List[StatusRead])
def get_statuses(db: Session = Depends(get_db)):
    return db.query(Status).all()
