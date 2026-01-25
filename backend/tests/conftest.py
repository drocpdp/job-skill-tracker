import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session

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
    Create a DB session wrapped in an outer transaction.
    Each test runs inside a SAVEPOINT so app-level rollbacks
    don't break the test harness teardown.
    """
    connection = test_engine.connect()
    outer_tx = connection.begin()

    session = Session(bind=connection, join_transaction_mode="create_savepoint")

    try:
        yield session
    finally:
        session.close()
        if outer_tx.is_active:
            outer_tx.rollback()
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