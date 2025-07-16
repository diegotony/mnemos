from sqlalchemy.orm import Session
from models.status import Status
from models.priority import Priority
from models.user import User
from datetime import date
import os
import logging
logger = logging.getLogger(__name__)


DEFAULT_STATUSES = ["active", "paused", "completed", "cancelled","draft","in progress","skiped"]
DEFAULT_PRIORITIES = ["low", "medium", "high"]

def init_statuses(db: Session):
    for name in DEFAULT_STATUSES:
        exists = db.query(Status).filter_by(name=name).first()
        if not exists:
            db.add(Status(name=name))
    db.commit()

def init_priorities(db):
    for name in DEFAULT_PRIORITIES:
        exists = db.query(Priority).filter_by(name=name).first()
        if not exists:
            db.add(Priority(name=name))
    db.commit()


def init_default_user(db: Session):
    name = os.getenv("DEFAULT_USER_NAME")
    email = os.getenv("DEFAULT_USER_EMAIL")
    birth = os.getenv("DEFAULT_USER_BIRTH")

    missing = []
    if not name:
        missing.append("DEFAULT_USER_NAME")
    if not email:
        missing.append("DEFAULT_USER_EMAIL")
    if not birth:
        missing.append("DEFAULT_USER_BIRTH")

    if missing:
        print(f"⚠️  Skipping default user creation. Missing: {', '.join(missing)}", flush=True)
        print("ℹ️  Set these variables in your .env file to auto-create a default user.", flush=True)
        logger.info("✅ Default user created")
        return

    existing = db.query(User).filter_by(email=email).first()
    if existing:
        print(f"👤 Default user '{email}' already exists (ID: {existing.id})", flush=True)
    try:
        birth_date = date.fromisoformat(birth)
    except ValueError:
        print("❌ Invalid format for DEFAULT_USER_BIRTH. Use YYYY-MM-DD.", flush=True)
        return

    user = User(
        name=name,
        email=email,
        birth_date=birth_date
    )

    db.add(user)
    db.commit()
    db.refresh(user)
    print(f"✅ Default user created: {user.name} (ID: {user.id})", flush=True)
    
