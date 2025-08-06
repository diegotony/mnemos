from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database import SessionLocal
from models.project import Project
from schemas.project import ProjectCreate, ProjectRead, ProjectUpdate

router = APIRouter(prefix="/projects", tags=["Projects"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post(
    "/",
    response_model=ProjectRead,
    status_code=status.HTTP_201_CREATED
)
def create_project(
    project: ProjectCreate,
    db: Session = Depends(get_db)
):
    db_proj = Project(**project.dict())
    db.add(db_proj)
    db.commit()
    db.refresh(db_proj)
    return db_proj

@router.get(
    "/",
    response_model=List[ProjectRead]
)
def get_projects(db: Session = Depends(get_db)):
    return db.query(Project).all()

@router.get(
    "/{project_id}",
    response_model=ProjectRead
)
def get_project(
    project_id: int,
    db: Session = Depends(get_db)
):
    proj = db.query(Project).filter(Project.id == project_id).first()
    if not proj:
        raise HTTPException(status_code=404, detail="Project not found")
    return proj

@router.put(
    "/{project_id}",
    response_model=ProjectRead
)
def update_project(
    project_id: int,
    project_in: ProjectUpdate,
    db: Session = Depends(get_db)
):
    proj = db.query(Project).filter(Project.id == project_id).first()
    if not proj:
        raise HTTPException(status_code=404, detail="Project not found")
    for field, value in project_in.dict(exclude_unset=True).items():
        setattr(proj, field, value)
    db.add(proj)
    db.commit()
    db.refresh(proj)
    return proj

@router.delete(
    "/{project_id}",
    response_model=ProjectRead
)
def delete_project(
    project_id: int,
    db: Session = Depends(get_db)
):
    proj = db.query(Project).filter(Project.id == project_id).first()
    if not proj:
        raise HTTPException(status_code=404, detail="Project not found")
    db.delete(proj)
    db.commit()
    return proj
