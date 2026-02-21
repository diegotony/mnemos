from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from models.idea import Idea
from schemas.idea import IdeaCreate, IdeaRead, IdeaUpdate
from dependencies.database import get_db

router = APIRouter(prefix="/ideas", tags=["Ideas"])


@router.post(
    "/",
    response_model=IdeaRead,
    status_code=status.HTTP_201_CREATED,
    response_model_exclude_none=True,
)
def create_idea(idea: IdeaCreate, db: Session = Depends(get_db)):
    db_idea = Idea(**idea.model_dump())
    db.add(db_idea)
    db.commit()
    db.refresh(db_idea)
    return db_idea


@router.get("/", response_model=List[IdeaRead], response_model_exclude_none=True)
def list_ideas(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Lista ideas con paginación.

    - **skip**: Número de registros a saltar (default: 0)
    - **limit**: Número máximo de registros a retornar (default: 100)
    """
    return db.query(Idea).offset(skip).limit(limit).all()


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
    for field, value in idea_in.model_dump(exclude_unset=True).items():
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
