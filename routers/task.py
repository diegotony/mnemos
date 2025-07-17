from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from models.task import Task
from schemas.task import TaskCreate, TaskRead, TaskUpdate
from typing import List, Optional
from utils.logger import logger
from dependencies.user import get_current_user_id
from models.time_bucket import TimeBucket
from datetime import date, timedelta
import calendar

router = APIRouter(prefix="/tasks", tags=["Tasks"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def calculate_due_date_from_slug(slug: str) -> Optional[date]:
    today = date.today()
    if slug == "today":
        return today
    elif slug == "tomorrow":
        return today + timedelta(days=1)
    elif slug == "this_week":
        weekday = today.weekday()  # lunes = 0
        return today + timedelta(days=(6 - weekday))
    elif slug == "this_month":
        last_day = calendar.monthrange(today.year, today.month)[1]
        return date(today.year, today.month, last_day)
    elif slug == "someday":
        return None
    return None



@router.post("/", response_model=TaskRead)
def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    logger.debug("Creating Task...")

    task_dict = task.dict()

    # Si no se envió due_date pero sí time_bucket_id, calcularlo
    if not task.due_date and task.time_bucket_id:
        bucket = db.query(TimeBucket).filter_by(id=task.time_bucket_id).first()
        if not bucket:
            raise HTTPException(status_code=404, detail="Time bucket not found")
        due_date = calculate_due_date_from_slug(bucket.slug)
        task_dict["due_date"] = due_date

    db_task = Task(**task_dict)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)

    logger.debug(f"Task created: {db_task}")
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
