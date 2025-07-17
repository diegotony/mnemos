from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import SessionLocal
from models.time_bucket import TimeBucket
from schemas.time_bucket import TimeBucketCreate, TimeBucketRead
from typing import List

router = APIRouter(prefix="/time-buckets", tags=["Time Buckets"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=TimeBucketRead)
def create_time_bucket(bucket: TimeBucketCreate, db: Session = Depends(get_db)):
    db_bucket = TimeBucket(**bucket.dict())
    db.add(db_bucket)
    db.commit()
    db.refresh(db_bucket)
    return db_bucket

@router.get("/", response_model=List[TimeBucketRead])
def get_time_buckets(db: Session = Depends(get_db)):
    return db.query(TimeBucket).all()
