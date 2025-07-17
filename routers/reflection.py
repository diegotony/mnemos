from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import SessionLocal
from models.reflection import Reflection
from schemas.reflection import ReflectionCreate, ReflectionRead
from typing import List
from utils.logger import logger
from dependencies.user import get_current_user_id


router = APIRouter(prefix="/reflections", tags=["Reflections"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=ReflectionRead)
def create_reflection(
    reflection: ReflectionCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    logger.debug("Creating Reflection...")
    db_reflection = Reflection(**reflection.dict(), user_id=user_id)
    logger.debug("Preparing Reflection...")
    db.add(db_reflection)
    db.commit()
    logger.debug("Executed 'Creating Reflection Transaction'...")
    logger.debug(f"Reflection before commit: {db_reflection}")
    db.refresh(db_reflection)
    logger.debug("Updated db_reflection")
    logger.debug(f"Reflection after refresh: {db_reflection}")
    return db_reflection


@router.get("/", response_model=List[ReflectionRead])
def get_reflections(db: Session = Depends(get_db)):
    return db.query(Reflection).all()
