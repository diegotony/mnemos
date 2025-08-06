from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from database import SessionLocal, Base, engine
from models import *
from routers import user, task, status, priority, project, area, inbox_item
from utils.seed import (
    init_statuses,
    init_priorities,
    init_default_user,
)
import os
from dotenv import load_dotenv
from sqlalchemy.exc import OperationalError
from sqlalchemy import text

load_dotenv()
Base.metadata.create_all(bind=engine)

API_V1 = "/api/v1"

app = FastAPI()
app.include_router(user.router, prefix=API_V1)
app.include_router(task.router, prefix=API_V1)
app.include_router(status.router, prefix=API_V1)
app.include_router(priority.router, prefix=API_V1)
app.include_router(project.router, prefix=API_V1)
app.include_router(area.router, prefix=API_V1)
app.include_router(inbox_item.router, prefix=API_V1)


@app.on_event("startup")
def startup_event():
    DEFAULT_USER_ID = os.getenv("DEFAULT_USER_ID")
    if DEFAULT_USER_ID:
        print(f"✅ Using default user ID: {DEFAULT_USER_ID}")
    else:
        print("⚠️  DEFAULT_USER_ID not set — the API expects user_id in requests.")
    db = SessionLocal()
    try:
        # Probar conexión a la base de datos
        db.execute(text("SELECT 1"))
        print("🗄️  Database connection successful.")

        # Inicializar tablas de catálogo
        init_statuses(db)
        init_priorities(db)
        init_default_user(db)
        print("📋 Statuses and priorities seeded.")
    except Exception as e:
        print(f"❌ Startup error: {e}", flush=True)

    except OperationalError:
        print("❌ Failed to connect to the database.")
    finally:
        db.close()


@app.get("/")
def hello():
    return {"message": "Hello World"}
