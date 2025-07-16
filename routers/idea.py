from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import SessionLocal
from models.idea import Idea
from schemas.idea import IdeaCreate, IdeaRead
from typing import List

router = APIRouter(prefix="/ideas", tags=["Ideas"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=IdeaRead)
def create_idea(idea: IdeaCreate, db: Session = Depends(get_db)):
    db_idea = Idea(**idea.dict())
    db.add(db_idea)
    db.commit()
    db.refresh(db_idea)
    return db_idea

@router.get("/", response_model=List[IdeaRead])
def get_ideas(db: Session = Depends(get_db)):
    return db.query(Idea).all()
