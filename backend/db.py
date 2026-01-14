import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker

# Load .env explicitly from backend/
load_dotenv(Path(__file__).parent / ".env")

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL not set")

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)

def get_db():
    """
    FastAPI dependency: provides one Session per request,
    and guarantees it closes
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def test_db_connection():
    """
    Simple health check: verifies DB is reachable.
    Uses a direct engine connection (not ORM session).
    """
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"ok": True}
    except SQLAlchemyError as e:
        return {"ok": False, "error":str(e)}