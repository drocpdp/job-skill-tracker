import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from db import get_db, test_db_connection
from models import Job
from schemas import JobCreate, JobRead, JobUpdate

# Load .env explicitly from this folder
load_dotenv(Path(__file__).parent / ".env")

app = FastAPI(title="Job Skill Tracker API")


@app.on_event("startup")
def startup_check():
    """
    Fail fast if DB isn't reachable at startup
    """
    result = test_db_connection()
    if not result.get("ok"):
        raise RuntimeError(f"Database connection failed: {result.get('error')}")

@app.get("/health")
def health():
    return {
        "status": "ok",
        "env_test": os.getenv("TEST_MESSAGE"),
        "database": test_db_connection(),
    }

@app.post("/jobs", response_model=JobRead, status_code=201)
def create_job(payload: JobCreate, db: Session = Depends(get_db)):
    job = Job(**payload.model_dump())
    db.add(job)
    db.commit()
    db.refresh(job)
    return job

@app.get("/jobs", response_model=list[JobRead])
def list_jobs(q: Optional[str] = None, db: Session = Depends(get_db)):
    stmt = select(Job)
    if q:
        stmt = stmt.where(or_(Job.company.ilike(f"%{q}%"), Job.title.ilike(f"%{q}%")))
    stmt = stmt.order_by(Job.id.desc())
    return list(db.execute(stmt).scalars().all())

@app.get("/jobs/{job_id}", response_model=JobRead)
def get_job(job_id: int, db: Session = Depends(get_db)):
    job = db.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

@app.patch("/jobs/{job_id}", response_model=JobRead)
def update_job(job_id: int, payload: JobUpdate, db: Session = Depends(get_db)):
    job = db.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    updates = payload.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(job, field, value)
    
    db.commit()
    db.refresh(job)
    return job