import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from backend.db import get_db
from backend import main


def _load_env_file(path: Path, *, override: bool) -> None:
    if not path.exists():
        return
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        k = k.strip()
        v = v.strip().strip('"').strip("'")
        if override:
            os.environ[k] = v
        else:
            os.environ.setdefault(k, v)


def pytest_configure() -> None:
    """
    Env selection for tests:

    - APP_ENV=test -> load backend/.env.test (override=True)
    - APP_ENV=dev  -> load backend/.env      (override=True)
    - APP_ENV not set -> do nothing (supports your old:
        export $(cat backend/.env.test | xargs) && pytest
      flow)
    """
    app_env = os.environ.get("APP_ENV", "").strip().lower()
    repo_root = Path(__file__).resolve().parents[2]
    backend_dir = repo_root / "backend"

    if app_env == "test":
        _load_env_file(backend_dir / ".env.test", override=True)
        assert "job_skill_tracker_test" in os.environ.get("DATABASE_URL", ""), os.environ.get("DATABASE_URL")
    elif app_env == "dev":
        _load_env_file(backend_dir / ".env", override=True)

    # Optional debug print
    print("[pytest] APP_ENV =", app_env or "<unset>", "DATABASE_URL =", os.environ.get("DATABASE_URL"))


@pytest.fixture(scope="session")
def test_engine():
    db_url = os.getenv("DATABASE_URL")
    assert db_url, "DATABASE_URL must be set (point it to job_skill_tracker_test)"
    return create_engine(db_url, pool_pre_ping=True)


@pytest.fixture()
def db_session(test_engine):
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
    def override_get_db():
        yield db_session

    main.app.dependency_overrides[get_db] = override_get_db
    with TestClient(main.app) as c:
        yield c
    main.app.dependency_overrides.clear()
