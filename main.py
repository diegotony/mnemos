from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from database import SessionLocal, Base, engine
from models import *
from routers import user, task, habit_log,reminder,habit, status, reflection
from utils.seed import init_statuses

Base.metadata.create_all(bind=engine)

db = SessionLocal()
init_statuses(db)
db.close()

app = FastAPI()
app.include_router(user.router)
app.include_router(task.router)
app.include_router(habit_log.router)
app.include_router(reminder.router)
app.include_router(habit_log.router)
app.include_router(status.router)
app.include_router(reflection.router)

# Dependency para inyectar sesión de BD
def get_db():
    db = SessionLocal()
    try:
        yield db
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