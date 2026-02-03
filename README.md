# Job Skill Tracker API (FastAPI + Postgres)

A personal “experience & skills” tracker built as a clean, testable REST API. The goal is to model job experiences, the skills used in those roles, and the relationships between them—so you can query, analyze, and grow a skills portfolio over time.

## What this is
- **FastAPI** backend with a **PostgreSQL** datastore
- Designed around real-world API patterns: validation, persistence, relational integrity, and automated tests
- Built for extensibility (migrations, environment separation, CI readiness, Docker support)

## Key capabilities
- Create and manage **Jobs / Experiences**
- Create and manage **Skills**
- Associate skills to jobs (many-to-many) with safe integrity rules
- Query and filter resources via REST endpoints
- Database schema managed through **Alembic migrations**
- Test suite with **pytest** (separate test database)

## Tech stack
- **Python**, **FastAPI**
- **SQLAlchemy** (ORM)
- **PostgreSQL**
- **Alembic** (migrations)
- **pytest** (tests)

## Architecture (high-level)
- API layer: FastAPI routes + Pydantic schemas
- Persistence: SQLAlchemy models + session management
- Migrations: Alembic for reproducible schema changes across environments
- Environments: separate `.env` (dev) and `.env.test` (tests)

## Quickstart (local, no Docker)

Typical flow:
1. Create and activate a venv
2. Install dependencies
3. Create `.env` and `.env.test`
4. Create dev/test databases
5. Run Alembic migrations
6. Run tests
7. Start the API

## Running tests
Tests run against the **test database** (configured in `backend/.env.test`):

    export $(cat backend/.env.test | xargs)
    pytest -v -s

## Docker
This project is designed to work well with Docker.

Recommended approach:
- Use **docker-compose** to orchestrate services (API + Postgres)
- Use a **Makefile** as a convenient wrapper for common commands (dev up/down, migrate, test)

A typical Docker workflow will look like:
- `docker compose up -d` (start Postgres + API)
- `docker compose exec api alembic upgrade head`
- `docker compose exec api pytest`

## Why this matters (engineering focus)
This project demonstrates:
- Proper modeling of relational data (many-to-many associations)
- Environment-safe configuration (dev vs test)
- Schema migration discipline to prevent drift
- Repeatable automation (tests, migrations, startup health checks)

## Roadmap (next steps)
- Docker-first dev workflow (`docker-compose.yml`)
- CI pipeline (GitHub Actions): lint + tests + migration checks
- Repository/service layer refactor for larger scale
- Additional entities (projects, achievements, tags, metrics)
- Optional frontend (React) for dashboards and analytics

## Screenshots / Demo
- To be added.

## License
Private / personal project
