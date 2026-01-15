import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.db import get_db
from backend import main

@pytest.fixture(scope="session")
def test_engine():
    db_url = os.getenv("DATABASE_URL")
    assert db_url, "DATABASE_URL must be set (point it to job_skill_tracker_test)"
    engine = create_engine(db_url, pool_pre_ping=True)
    return engine

@pytest.fixture()
def db_session(test_engine):
    """
    Create a DB session wrapped in a transaction, rolled back after each test.
    """
    connection = test_engine.connect()
    transaction = connection.begin()

    TestingSessionLocal = sessionmaker(bind=connection, autoflush=False, autocommit=False)
    session = TestingSessionLocal()

    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()
    
@pytest.fixture()
def client(db_session):
    """
    FastAPI TestClient that uses the test DB session via dependency override.
    """
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    main.app.dependency_overrides[get_db] = override_get_db
    with TestClient(main.app) as c:
        yield c
    main.app.dependency_overrides.clear()