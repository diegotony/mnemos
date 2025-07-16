from sqlalchemy.orm import Session
from models.status import Status

DEFAULT_STATUSES = ["active", "paused", "completed", "cancelled"]

def init_statuses(db: Session):
    for name in DEFAULT_STATUSES:
        exists = db.query(Status).filter_by(name=name).first()
        if not exists:
            db.add(Status(name=name))
    db.commit()
