from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from models.task import Task
from schemas.task import TaskCreate, TaskRead
from typing import List

router = APIRouter(prefix="/tasks", tags=["Tasks"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=TaskRead)
def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    db_task = Task(**task.dict())
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

@router.get("/", response_model=List[TaskRead])
def get_tasks(db: Session = Depends(get_db)):
    return db.query(Task).all()
