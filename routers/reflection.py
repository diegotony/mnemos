from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import SessionLocal
from models.reflection import Reflection
from schemas.reflection import ReflectionCreate, ReflectionRead
from typing import List

router = APIRouter(prefix="/reflections", tags=["Reflections"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=ReflectionRead)
def create_reflection(reflection: ReflectionCreate, db: Session = Depends(get_db)):
    db_reflection = Reflection(**reflection.dict())
    db.add(db_reflection)
    db.commit()
    db.refresh(db_reflection)
    return db_reflection

@router.get("/", response_model=List[ReflectionRead])
def get_reflections(db: Session = Depends(get_db)):
    return db.query(Reflection).all()
