from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from database import SessionLocal, Base, engine
from models import *
from routers import user, status, priority, inbox_item, idea, calendar, analytics
from utils.seed import (
    init_statuses,
    init_priorities,
    init_default_user,
)
from utils.logger import logger
from utils.telemetry import setup_opentelemetry, instrument_fastapi
from utils.config import get_priority_config
import os
from dotenv import load_dotenv
from sqlalchemy.exc import OperationalError
from sqlalchemy import text

load_dotenv()

# Setup OpenTelemetry BEFORE creating FastAPI app
setup_opentelemetry()

Base.metadata.create_all(bind=engine)

API_V1 = "/api/v1"

app = FastAPI(
    title="Mnemos API",
    description="""
# Personal Time Management System

API para gestionar tu tiempo, ideas e inbox con sincronización a Google Calendar.

## 🎨 Categorías con Colores

Los eventos se colorean automáticamente en Google Calendar según su categoría:

- 🔵 **TRABAJO** → Azul (Arándano)
- 🟢 **SALUD** → Verde (Albahaca)  
- 🔴 **OCIO** → Rojo (Tomate)
- 🟡 **RUTINA** → Amarillo (Banana)
- 💜 **PERSONAL** → Lavanda
- 🔷 **ESTUDIO** → Cyan (Pavo real)
- 🌸 **FAMILIA** → Rosado (Flamingo)
- 🟣 **SOCIAL** → Púrpura (Uva)

Ver `/api/v1/calendar/categories` para más detalles.

## 📚 Documentación

- [Guía de Uso de Calendar API](https://github.com/tu-usuario/mnemos/blob/main/docs/CALENDAR_API_USAGE.md)
- [Integración con Google Calendar](https://github.com/tu-usuario/mnemos/blob/main/docs/GOOGLE_CALENDAR_INTEGRATION.md)
    """,
    version="1.1.0",
)

# Instrument FastAPI with OpenTelemetry
instrument_fastapi(app)
app.include_router(user.router, prefix=API_V1)
app.include_router(status.router, prefix=API_V1)
app.include_router(priority.router, prefix=API_V1)
app.include_router(inbox_item.router, prefix=API_V1)
app.include_router(idea.router, prefix=API_V1)
app.include_router(calendar.router, prefix=API_V1)
app.include_router(analytics.router, prefix=API_V1)


@app.on_event("startup")
def startup_event():
    DEFAULT_USER_ID = os.getenv("DEFAULT_USER_ID")
    if DEFAULT_USER_ID:
        logger.info(f"✅ Using default user ID: {DEFAULT_USER_ID}")
    else:
        logger.warning(
            "⚠️  DEFAULT_USER_ID not set — the API expects user_id in requests."
        )

    # Validar configuración de priorización
    logger.info("🔧 Validando configuración de priorización...")
    priority_config = get_priority_config()

    db = SessionLocal()
    try:
        # Probar conexión a la base de datos
        db.execute(text("SELECT 1"))
        logger.info("🗄️  Database connection successful.")

        # Inicializar tablas de catálogo
        init_statuses(db)
        init_priorities(db)
        init_default_user(db)
        logger.info("📋 Statuses and priorities seeded.")
    except OperationalError as e:
        logger.error(f"❌ Failed to connect to the database: {e}")
    except Exception as e:
        logger.error(f"❌ Startup error: {e}")
    finally:
        db.close()


@app.get("/")
def hello():
    return {"message": "Hello World"}
