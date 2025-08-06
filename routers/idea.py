from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database import SessionLocal
from models.idea import Idea
from schemas.idea import IdeaCreate, IdeaRead, IdeaUpdate

router = APIRouter(prefix="/ideas", tags=["Ideas"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post(
    "/",
    response_model=IdeaRead,
    status_code=status.HTTP_201_CREATED,
    response_model_exclude_none=True,
)
def create_idea(idea: IdeaCreate, db: Session = Depends(get_db)):
    db_idea = Idea(**idea.dict())
    db.add(db_idea)
    db.commit()
    db.refresh(db_idea)
    return db_idea


@router.get("/", response_model=List[IdeaRead], response_model_exclude_none=True)
def list_ideas(db: Session = Depends(get_db)):
    return db.query(Idea).all()


@router.get("/{idea_id}", response_model=IdeaRead, response_model_exclude_none=True)
def get_idea(idea_id: int, db: Session = Depends(get_db)):
    db_idea = db.query(Idea).filter(Idea.id == idea_id).first()
    if not db_idea:
        raise HTTPException(status_code=404, detail="Idea not found")
    return db_idea


@router.put("/{idea_id}", response_model=IdeaRead, response_model_exclude_none=True)
def update_idea(idea_id: int, idea_in: IdeaUpdate, db: Session = Depends(get_db)):
    db_idea = db.query(Idea).filter(Idea.id == idea_id).first()
    if not db_idea:
        raise HTTPException(status_code=404, detail="Idea not found")
    for field, value in idea_in.dict(exclude_unset=True).items():
        setattr(db_idea, field, value)
    db.add(db_idea)
    db.commit()
    db.refresh(db_idea)
    return db_idea


@router.delete("/{idea_id}", response_model=IdeaRead, response_model_exclude_none=True)
def delete_idea(idea_id: int, db: Session = Depends(get_db)):
    db_idea = db.query(Idea).filter(Idea.id == idea_id).first()
    if not db_idea:
        raise HTTPException(status_code=404, detail="Idea not found")
    db.delete(db_idea)
    db.commit()
    return db_idea
