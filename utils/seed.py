from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from models.status import Status
from models.priority import Priority
from models.user import User
from utils.logger import logger
from datetime import date
import os

DEFAULT_STATUSES = [
    "active",
    "paused",
    "completed",
    "cancelled",
    "draft",
    "in progress",
    "skiped",
]
DEFAULT_PRIORITIES = ["low", "medium", "high", "none"]
DEFAULT_TIME_BUCKETS = [
    {"name": "Hoy", "slug": "today"},
    {"name": "Mañana", "slug": "tomorrow"},
    {"name": "Esta semana", "slug": "this_week"},
    {"name": "Este mes", "slug": "this_month"},
    {"name": "Algún día", "slug": "someday"},
]


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


# def init_categories(db):
#     for name in DEFAULT_CATEGORIES:
#         exists = db.query(Category).filter_by(name=name).first()
#         if not exists:
#             db.add(Category(name=name))
#     db.commit()


# def init_time_buckets(db: Session):
#     for bucket in DEFAULT_TIME_BUCKETS:
#         exists = db.query(TimeBucket).filter_by(slug=bucket["slug"]).first()
#         if not exists:
#             db.add(TimeBucket(**bucket))
#     db.commit()


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
        logger.warning(
            f"⚠️  Skipping default user creation. Missing: {', '.join(missing)}"
        )
        return

    email = email.strip().lower()  # 🔍 limpieza extra

    existing = db.query(User).filter(User.email == email).first()
    if existing:
        logger.info(f"👤 Default user '{email}' already exists (ID: {existing.id})")
        return

    try:
        birth_date = date.fromisoformat(birth)
    except ValueError:
        logger.error("❌ DEFAULT_USER_BIRTH must be in format YYYY-MM-DD")
        return

    user = User(name=name.strip(), email=email, birth_date=birth_date)

    db.add(user)
    try:
        db.commit()
        db.refresh(user)
        logger.info(f"✅ Default user created: {user.name} (ID: {user.id})")
    except IntegrityError:
        db.rollback()
        logger.error("❌ Could not create user. It may already exist.")
