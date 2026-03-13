
# Job Skill Tracker API (FastAPI + Postgres)

Job Skill Tracker is a backend API that models professional experience as structured data. It tracks jobs, skills, and how these skills were used across roles -- allowing a developer's career portfolio to be queried and analyzed programatically.

## Technologies Demonstrated

FastAPI • Python • PostgreSQL • SQLAlchemy • Alembic • pytest • Docker-ready architecture • REST API design

## Features

* REST API for managing job experience and skills
* Many-to-many relational modeling (jobs ↔ skills)
* Data validation using Pydantic schemas
* Database migrations with Alembic
* Environment isolation (separate dev and test databases)
* Automated test suite with pytest


## Example API Endpoints

### <u>POST - /jobs (create job)</u>

<details>

###### Request Body
```
{
  "company": "string",
  "title": "string",
  "location": "string",
  "start_date": "2026-03-13",
  "end_date": "2026-03-13",
  "summary": "string",
  "notes": "string"
}
```
###### Successful Response
```
{
  "company": "string",
  "title": "string",
  "location": "string",
  "start_date": "2026-03-13",
  "end_date": "2026-03-13",
  "summary": "string",
  "notes": "string",
  "id": 0
}
```
</details>

### <u>GET - /jobs (list jobs)</u>

<details>

###### Request queries
```
GET /jobs?q=pyth
GET /jobs?skill=python
GET /jobs?skill_id=34
```
###### Successful Response
```
[
  {
    "company": "string",
    "title": "string",
    "location": "string",
    "start_date": "2026-03-13",
    "end_date": "2026-03-13",
    "summary": "string",
    "notes": "string",
    "id": 0
  }
]
```
</details>


### <u>POST ---- /skills</u>
### <u>GET /skills</u>
### <u>POST /jobs/{job_id}/skills - Attach skill to job</u>


## Engineering Practices Demonstrated

* Clean API architecture (routing, schema, persistence layers)
* Relational database modeling
* Database migrations with Alembic
* Environment-based configuration
* Automated testing with isolated test database
* Container-ready development workflow

## Why I Built This

As a QA automation engineer, I’ve worked with many complex systems but wanted a project that demonstrates backend API design, relational data modeling, and disciplined database migrations.

This project models a professional career as structured data that can be queried, analyzed, and extended over time.

## Example Use Cases

• Query which technologies were used in each role  
• Identify the most frequently used skills across a career  
• Track how skill usage evolves over time  
• Generate structured data for tailored resumes or portfolio analysis

## Tech stack
- **Python**, **FastAPI**
- **SQLAlchemy** (ORM)
- **PostgreSQL**
- **Alembic** (migrations)
- **pytest** (tests)

## Project Structure
```
backend/
  main.py            # FastAPI entry point
  models/            # SQLAlchemy models
  schemas/           # Pydantic schemas
  routers/           # API endpoints
  migrations/        # Alembic migration history
tests/               # pytest suite
```

## Architecture (high-level)
- API layer: FastAPI routes + Pydantic schemas
- Persistence: SQLAlchemy models + session management
- Migrations: Alembic for reproducible schema changes across environments
- Environments: separate `.env` (dev) and `.env.test` (tests)


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

## Roadmap (next steps)
- Docker-first dev workflow (`docker-compose.yml`)
- CI pipeline with GitHub Actions
- Repository/service layer refactor for larger scale
- Additional entities (projects, achievements, tags, metrics)
- Frontend (React) for dashboards and analytics
- Skill analytics queries

## Future analytics capabilities:

- Which skills appear most often across roles
- Skill growth over time
- Querying experience by technology stack

## Screenshots / Demo
- To be added.

## License
Private / personal project
