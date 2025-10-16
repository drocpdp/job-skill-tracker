# app/database.py
from sqlmodel import SQLModel, create_engine, Session

DATABASE_URL = "sqlite:///.local.db"
engine = create_engine(DATABASE_URL, echo=False, connect_args={"check_same_thread": False})

def create_db_and_tables():
    from app import models # ensures models are imported
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session