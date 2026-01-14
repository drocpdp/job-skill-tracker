import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import or_, select, and_
from sqlalchemy.orm import Session

from db import get_db, test_db_connection
from models import Job, Skill, JobSkill
from schemas import (
    JobCreate, JobRead, JobUpdate,
    SkillCreate, SkillRead,
    JobSkillUpsert, JobSkillRead
)


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


@app.post("/jobs/{job_id}/skills", response_model=JobSkillRead, status_code=201)
def attach_skill_to_job(job_id: int, payload: JobSkillUpsert, db: Session = Depends(get_db)):
    # 1) Ensure job exists
    job = db.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # 2) Resolve skill either by id or by name (create if needed)
    skill: Skill | None = None

    if payload.skill_id is not None:
        skill = db.get(Skill, payload.skill_id)
        if not skill:
            raise HTTPException(status_code=404, detail="Skill not found")
    else:
        if payload.skill is None or not payload.skill.name.strip():
            raise HTTPException(
                status_code=422,
                detail="Provide either skill_id or skill { name, ... }",
            )
        name = payload.skill.name.strip()

        # Try find by unique name
        skill = db.execute(select(Skill).where(Skill.name == name)).scalar_one_or_none()

        # Create if not found
        if not skill:
            skill = Skill(
                name=name, 
                category=payload.skill.category,
                notes=payload.skill.notes,
            )
            db.add(skill)
            db.commit()
            db.refresh(skill)
    
    # 3) Upsert association row (prevent duplicates)
    existing = db.execute(
        select(JobSkill).where(and_(JobSkill.job_id == job_id, JobSkill.skill_id == skill.id))
    ).scalar_one_or_none()

    if existing:
        # Update how_used if provided
        if payload.how_used is not None:
            existing.how_used = payload.how_used
            db.commit()
            db.refresh(existing)
        job_skill = existing
    else:
        job_skill = JobSkill(job_id=job_id, skill_id=skill.id, how_used=payload.how_used)
        db.add(job_skill)
        db.commit()
        db.refresh(job_skill)
    
    return {"skill": skill, "how_used": job_skill.how_used}
    

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

@app.get("/jobs/{job_id}/skills", response_model=list[JobSkillRead])
def list_job_skills(job_id: int, db: Session = Depends(get_db)):
    job = db.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    rows = db.execute(
        select(JobSkill, Skill)
        .join(Skill, Skill.id == JobSkill.skill_id)
        .where(JobSkill.job_id == job_id)
        .order_by(Skill.name.asc())
    ).all()

    return [{"skill": skill, "how_used": job_skill.how_used} for job_skill, skill in rows]


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


@app.delete("/jobs/{job_id}", status_code=204)
def delete_job(job_id: int, db: Session = Depends(get_db)):
    job = db.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    db.delete(job)
    db.commit()
    return None

@app.delete("/jobs/{job_id}/skills/{skill_id}", status_code=204)
def detach_skill_from_job(job_id: int, skill_id: int, db: Session = Depends(get_db)):
    assoc = db.execute(
        select(JobSkill).where(and_(JobSkill.job_id == job_id, JobSkill.skill_id == skill_id))
    ).scalar_one_or_none()

    if not assoc:
        raise HTTPException(status_code=404, detail="Job-skill link not found")
    
    db.delete(assoc)
    db.commit()
    return None