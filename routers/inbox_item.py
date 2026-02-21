# routers/inbox.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from models.inbox_item import InboxItem, SourceType as SourceEnum
from models.status import Status
from schemas.inbox_item import InboxItemCreate, InboxItemRead, InboxItemUpdate
from dependencies.database import get_db

router = APIRouter(prefix="/inbox", tags=["Inbox"])


@router.post(
    "/",
    response_model=InboxItemRead,
    status_code=status.HTTP_201_CREATED,
    response_model_exclude_none=True,
)
def create_inbox_item(item: InboxItemCreate, db: Session = Depends(get_db)):
    db_item = InboxItem(**item.model_dump())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


@router.get("/", response_model=List[InboxItemRead], response_model_exclude_none=True)
def list_inbox_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Lista inbox items con paginación.

    - **skip**: Número de registros a saltar (default: 0)
    - **limit**: Número máximo de registros a retornar (default: 100)
    """
    return db.query(InboxItem).offset(skip).limit(limit).all()


@router.get(
    "/{item_id}", response_model=InboxItemRead, response_model_exclude_none=True
)
def get_inbox_item(item_id: int, db: Session = Depends(get_db)):
    db_item = db.query(InboxItem).filter(InboxItem.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Inbox item not found")
    return db_item


@router.put(
    "/{item_id}",
    response_model=InboxItemRead,
    response_model_exclude_none=True,
)
def update_inbox_item(
    item_id: int, item_in: InboxItemUpdate, db: Session = Depends(get_db)
):
    db_item = db.query(InboxItem).filter(InboxItem.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Inbox item not found")

    # Validar status_id si se está actualizando
    update_data = item_in.model_dump(exclude_unset=True)
    if "status_id" in update_data and update_data["status_id"] is not None:
        status_exists = (
            db.query(Status).filter(Status.id == update_data["status_id"]).first()
        )
        if not status_exists:
            raise HTTPException(status_code=400, detail="Status ID does not exist")

    for field, value in update_data.items():
        setattr(db_item, field, value)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


@router.delete(
    "/{item_id}", response_model=InboxItemRead, response_model_exclude_none=True
)
def delete_inbox_item(item_id: int, db: Session = Depends(get_db)):
    db_item = db.query(InboxItem).filter(InboxItem.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Inbox item not found")
    db.delete(db_item)
    db.commit()
    return db_item
