from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import SessionLocal
from models.user import User
from schemas.user import UserCreate, UserRead
from typing import List

router = APIRouter(prefix="/users", tags=["Users"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=UserRead)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = User(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.get("/", response_model=List[UserRead])
def get_users(db: Session = Depends(get_db)):
    return db.query(User).all()
