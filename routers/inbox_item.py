# routers/inbox.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database import SessionLocal
from models.inbox_item import InboxItem, SourceType as SourceEnum
from schemas.inbox_item import (
    InboxItemCreate,
    InboxItemRead,
    InboxItemUpdate
)

router = APIRouter(prefix="/inbox", tags=["Inbox"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post(
    "/",
    response_model=InboxItemRead,
    status_code=status.HTTP_201_CREATED,
    response_model_exclude_none=True
)
def create_inbox_item(
    item: InboxItemCreate,
    db: Session = Depends(get_db)
):
    db_item = InboxItem(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@router.get(
    "/",
    response_model=List[InboxItemRead],
    response_model_exclude_none=True
)
def list_inbox_items(db: Session = Depends(get_db)):
    return db.query(InboxItem).all()

@router.get(
    "/{item_id}",
    response_model=InboxItemRead,
    response_model_exclude_none=True
)
def get_inbox_item(item_id: int, db: Session = Depends(get_db)):
    db_item = db.query(InboxItem).filter(InboxItem.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Inbox item not found")
    return db_item

@router.put(
    "/{item_id}",
    response_model=InboxItemRead,
    response_model_exclude_none=True
)
def update_inbox_item(
    item_id: int,
    item_in: InboxItemUpdate,
    db: Session = Depends(get_db)
):
    db_item = db.query(InboxItem).filter(InboxItem.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Inbox item not found")
    for field, value in item_in.dict(exclude_unset=True).items():
        setattr(db_item, field, value)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@router.delete(
    "/{item_id}",
    response_model=InboxItemRead,
    response_model_exclude_none=True
)
def delete_inbox_item(item_id: int, db: Session = Depends(get_db)):
    db_item = db.query(InboxItem).filter(InboxItem.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Inbox item not found")
    db.delete(db_item)
    db.commit()
    return db_item
