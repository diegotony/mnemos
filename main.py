from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from database import SessionLocal, Base, engine
from models import *
from routers import (
    user,
    task,
    habit_log,
    reminder,
    habit,
    status,
    reflection,
    priority,
    idea,
    category,
    time_bucket
)
from utils.seed import (
    init_statuses,
    init_priorities,
    init_default_user,
    init_categories,
    init_time_buckets
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
app.include_router(habit_log.router, prefix=API_V1)
app.include_router(reminder.router, prefix=API_V1)
app.include_router(habit_log.router, prefix=API_V1)
app.include_router(status.router, prefix=API_V1)
app.include_router(reflection.router, prefix=API_V1)
app.include_router(priority.router, prefix=API_V1)
app.include_router(idea.router, prefix=API_V1)
app.include_router(category.router, prefix=API_V1)
app.include_router(time_bucket.router, prefix=API_V1)


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
        init_categories(db)
        init_time_buckets(db)
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


# @app.post("/usuarios/")
# def crear_usuario(nombre: str, email: str, db: Session = Depends(get_db)):
#     nuevo_usuario = Usuario(nombre=nombre, email=email)
#     db.add(nuevo_usuario)
#     db.commit()
#     db.refresh(nuevo_usuario)
#     return nuevo_usuario
