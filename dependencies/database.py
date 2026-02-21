from database import SessionLocal


def get_db():
    """
    Dependency para obtener una sesión de base de datos.
    Se usa en todos los endpoints que necesitan acceso a la DB.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
