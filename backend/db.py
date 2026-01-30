# backend/db.py
import os
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker

_engine = None
_SessionLocal = None

def _init_engine_if_needed():
    global _engine, _SessionLocal
    if _engine is not None:
        return

    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL not set")

    _engine = create_engine(database_url, pool_pre_ping=True)
    _SessionLocal = sessionmaker(bind=_engine, autoflush=False, autocommit=False)

def get_db():
    _init_engine_if_needed()
    db = _SessionLocal()
    try:
        yield db
    finally:
        db.close()

def test_db_connection():
    try:
        _init_engine_if_needed()
        with _engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"ok": True, "database_url": os.getenv("DATABASE_URL")}
    except SQLAlchemyError as e:
        return {"ok": False, "error": str(e), "database_url": os.getenv("DATABASE_URL")}
