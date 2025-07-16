import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Usa SQLite por defecto, pero permite sobreescribir con una variable de entorno
DATABASE_URL = os.getenv(
    "DATABASE_URL", "sqlite:///./db.sqlite3"
)

# Configuración especial para SQLite
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()
