from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from models.task import Task
from schemas.task import TaskCreate, TaskRead, TaskUpdate
from typing import List
from utils.logger import logger
from dependencies.user import get_current_user_id

router = APIRouter(prefix="/tasks", tags=["Tasks"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=TaskRead)
def create_task(
    task: TaskCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    logger.debug("Creating Task...")
    db_task = Task(**task.dict(), user_id=user_id)
    logger.debug("Preparing Creating Task...")
    db.add(db_task)
    db.commit()
    logger.debug("Executed 'Creating Task Transaction'...")
    logger.debug(f"Task before commit: {db_task}")
    db.refresh(db_task)
    logger.debug("Updated db_task")
    logger.debug(f"Task after refresh: {db_task}")
    return db_task


@router.get("/", response_model=List[TaskRead])
def get_tasks(db: Session = Depends(get_db)):
    return db.query(Task).all()


@router.put("/{task_id}", response_model=TaskRead)
def update_task(task_id: int, task_update: TaskUpdate, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    for field, value in task_update.dict(exclude_unset=True).items():
        setattr(task, field, value)

    db.commit()
    db.refresh(task)
    return task
