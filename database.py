import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base


def validate_env_var(var_name: str, value: str | None, db_type: str) -> str:
    """Valida que una variable de entorno requerida exista y no esté vacía."""
    if not value or value.strip() == "":
        print(
            f"\n❌ ERROR: Variable de entorno '{var_name}' requerida para DB_TYPE={db_type}"
        )
        print(f"💡 Solución: Agrega '{var_name}' a tu archivo .env")
        print(f"\nEjemplo en .env:")
        if db_type == "postgresql":
            print(f"""
DB_TYPE=postgresql
POSTGRES_USER=mnemos_user
POSTGRES_PASSWORD=tu_contraseña_segura
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=mnemos_db
""")
        print(f"\n📚 Ver docs/DATABASE_SETUP.md para más información\n")
        sys.exit(1)
    return value


# Tipo de base de datos (sqlite o postgresql)
DB_TYPE = os.getenv("DB_TYPE", "sqlite").lower()

# Validar que DB_TYPE sea válido
if DB_TYPE not in ["sqlite", "postgresql"]:
    print(f"\n❌ ERROR: DB_TYPE='{DB_TYPE}' no es válido")
    print(f"💡 Valores permitidos: 'sqlite' o 'postgresql'")
    print(f"\nEjemplo en .env:")
    print(f"DB_TYPE=sqlite   # Para SQLite")
    print(f"DB_TYPE=postgresql   # Para PostgreSQL\n")
    sys.exit(1)

# Configuración automática según DB_TYPE
if DB_TYPE == "postgresql":
    # PostgreSQL: validar variables requeridas
    PG_USER = validate_env_var(
        "POSTGRES_USER", os.getenv("POSTGRES_USER"), "postgresql"
    )
    PG_PASSWORD = validate_env_var(
        "POSTGRES_PASSWORD", os.getenv("POSTGRES_PASSWORD"), "postgresql"
    )
    PG_HOST = validate_env_var(
        "POSTGRES_HOST", os.getenv("POSTGRES_HOST"), "postgresql"
    )
    PG_PORT = validate_env_var(
        "POSTGRES_PORT", os.getenv("POSTGRES_PORT"), "postgresql"
    )
    PG_DB = validate_env_var("POSTGRES_DB", os.getenv("POSTGRES_DB"), "postgresql")

    # Construir URL de conexión
    DATABASE_URL = f"postgresql://{PG_USER}:{PG_PASSWORD}@{PG_HOST}:{PG_PORT}/{PG_DB}"
    connect_args = {}
    engine_args = {
        "pool_size": int(os.getenv("DB_POOL_SIZE", "10")),
        "max_overflow": int(os.getenv("DB_MAX_OVERFLOW", "20")),
        "pool_pre_ping": True,
        "pool_recycle": 3600,
    }

    print(f"✅ PostgreSQL configurado: {PG_USER}@{PG_HOST}:{PG_PORT}/{PG_DB}")
else:
    # SQLite (por defecto)
    SQLITE_PATH = os.getenv("SQLITE_PATH", "./db.sqlite3")
    DATABASE_URL = f"sqlite:///{SQLITE_PATH}"
    connect_args = {"check_same_thread": False}
    engine_args = {}

    print(f"✅ SQLite configurado: {SQLITE_PATH}")

# Crear engine con configuración apropiada
try:
    engine = create_engine(DATABASE_URL, connect_args=connect_args, **engine_args)
    SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    Base = declarative_base()
except Exception as e:
    print(f"\n❌ ERROR: No se pudo conectar a la base de datos")
    print(f"📋 Detalles: {str(e)}")
    print(f"\n💡 Verificaciones:")
    if DB_TYPE == "postgresql":
        print(f"   - PostgreSQL está corriendo?")
        print(f"   - Las credenciales son correctas?")
        print(f"   - La base de datos '{os.getenv('POSTGRES_DB')}' existe?")
        print(f"\n📚 Ver docs/DATABASE_SETUP.md para troubleshooting\n")
    else:
        print(f"   - El directorio para el archivo SQLite existe?")
        print(f"   - Tienes permisos de escritura?\n")
    sys.exit(1)
