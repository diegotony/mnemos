from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from models.user import User
from schemas.user import UserCreate, UserRead
from dependencies.database import get_db
from typing import List

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/", response_model=UserRead)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = User(**user.model_dump())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@router.get("/", response_model=List[UserRead])
def get_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Lista usuarios con paginación.

    - **skip**: Número de registros a saltar (default: 0)
    - **limit**: Número máximo de registros a retornar (default: 100)
    """
    return db.query(User).offset(skip).limit(limit).all()
