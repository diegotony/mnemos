from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database import SessionLocal
from models.project import Project  # tu clase Project sobre la tabla "areas"
from schemas.area import AreaCreate, AreaRead, AreaUpdate

router = APIRouter(prefix="/areas", tags=["Areas"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=AreaRead, status_code=status.HTTP_201_CREATED)
def create_area(area: AreaCreate, db: Session = Depends(get_db)):
    db_area = Project(**area.dict())
    db.add(db_area)
    db.commit()
    db.refresh(db_area)
    return db_area


@router.get("/", response_model=List[AreaRead])
def get_areas(db: Session = Depends(get_db)):
    return db.query(Project).all()


@router.get("/{area_id}", response_model=AreaRead)
def get_area(area_id: int, db: Session = Depends(get_db)):
    db_area = db.query(Project).filter(Project.id == area_id).first()
    if not db_area:
        raise HTTPException(status_code=404, detail="Area not found")
    return db_area


@router.put("/{area_id}", response_model=AreaRead)
def update_area(area_id: int, area_in: AreaUpdate, db: Session = Depends(get_db)):
    db_area = db.query(Project).filter(Project.id == area_id).first()
    if not db_area:
        raise HTTPException(status_code=404, detail="Area not found")
    for field, value in area_in.dict(exclude_unset=True).items():
        setattr(db_area, field, value)
    db.add(db_area)
    db.commit()
    db.refresh(db_area)
    return db_area


@router.delete("/{area_id}", response_model=AreaRead)
def delete_area(area_id: int, db: Session = Depends(get_db)):
    db_area = db.query(Project).filter(Project.id == area_id).first()
    if not db_area:
        raise HTTPException(status_code=404, detail="Area not found")
    db.delete(db_area)
    db.commit()
    return db_area
