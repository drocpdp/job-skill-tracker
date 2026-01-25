import os
from pathlib import Path
from typing import Optional

from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import or_, select, and_
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from backend.db import get_db, test_db_connection
from backend.models import Job, Skill, JobSkill
from backend.schemas import (
    JobCreate, JobRead, JobUpdate,
    SkillCreate, SkillRead,
    JobSkillUpsert, JobSkillRead,
    SkillJobRead,
    # NEW:
    SkillUpdate,
    JobSkillUpdate,
)

# Load .env explicitly from this folder
load_dotenv(Path(__file__).parent / ".env")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Fail fast if DB isn't reachable at startup
    """
    result = test_db_connection()
    if not result.get("ok"):
        raise RuntimeError(f"Database connection failed: {result.get('error')}")
    yield


app = FastAPI(lifespan=lifespan, title="Job Skill Tracker API")


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
    """
    Option B: create-only.
    - Creates a JobSkill link if it doesn't exist.
    - Returns 409 if the link already exists.
    """
    # 1) Ensure job exists
    job = db.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # 2) Resolve skill either by id OR by name (create if needed)
    skill: Skill | None = None

    if payload.skill_id is not None:
        skill = db.get(Skill, payload.skill_id)
        if not skill:
            raise HTTPException(status_code=404, detail="Skill not found")
    else:
        if payload.skill is None or not payload.skill.name or not payload.skill.name.strip():
            raise HTTPException(status_code=422, detail="Provide either skill_id or skill { name, ... }")

        name = payload.skill.name.strip()

        skill = db.execute(select(Skill).where(Skill.name == name)).scalar_one_or_none()

        if not skill:
            skill = Skill(
                name=name,
                category=payload.skill.category,
                notes=payload.skill.notes,
            )
            db.add(skill)
            db.commit()
            db.refresh(skill)

    # 3) Create-only association: reject duplicates
    existing = db.execute(
        select(JobSkill).where(and_(JobSkill.job_id == job_id, JobSkill.skill_id == skill.id))
    ).scalar_one_or_none()

    if existing:
        raise HTTPException(status_code=409, detail="Skill already attached to this job")

    job_skill = JobSkill(job_id=job_id, skill_id=skill.id, how_used=payload.how_used)
    db.add(job_skill)
    db.commit()
    db.refresh(job_skill)

    return {"skill": skill, "how_used": job_skill.how_used}


@app.patch("/jobs/{job_id}/skills/{skill_id}", response_model=JobSkillRead)
def update_job_skill(job_id: int, skill_id: int, payload: JobSkillUpdate, db: Session = Depends(get_db)):
    """
    Option B: update-only for association fields (e.g., how_used).
    """
    assoc = db.execute(
        select(JobSkill).where(and_(JobSkill.job_id == job_id, JobSkill.skill_id == skill_id))
    ).scalar_one_or_none()

    if not assoc:
        raise HTTPException(status_code=404, detail="Job-skill link not found")

    if payload.how_used is not None:
        assoc.how_used = payload.how_used.strip()

    db.commit()
    db.refresh(assoc)

    skill = db.get(Skill, skill_id)
    return {"skill": skill, "how_used": assoc.how_used}


@app.post("/skills", response_model=SkillRead, status_code=201)
def create_skill(payload: SkillCreate, db: Session = Depends(get_db)):
    name = payload.name.strip()
    if not name:
        raise HTTPException(status_code=422, detail="Skill name cannot be empty")

    existing = db.execute(select(Skill).where(Skill.name == name)).scalar_one_or_none()
    if existing:
        return existing

    skill = Skill(name=name, category=payload.category, notes=payload.notes)
    db.add(skill)
    db.commit()
    db.refresh(skill)
    return skill


@app.patch("/skills/{skill_id}", response_model=SkillRead)
def update_skill(skill_id: int, payload: SkillUpdate, db: Session = Depends(get_db)):
    """
    Updates skill fields (name/category/notes).
    """
    skill = db.get(Skill, skill_id)
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")

    if payload.name is not None:
        new_name = payload.name.strip()
        if not new_name:
            raise HTTPException(status_code=422, detail="Skill name cannot be empty")

        # Fast conflict check (nice error message)
        conflict = db.execute(
            select(Skill).where(Skill.name == new_name, Skill.id != skill_id)
        ).scalar_one_or_none()
        if conflict:
            raise HTTPException(status_code=409, detail="Skill name already exists")

        skill.name = new_name

    if payload.category is not None:
        skill.category = payload.category

    if payload.notes is not None:
        skill.notes = payload.notes

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Skill name already exists")

    db.refresh(skill)
    return skill


@app.get("/skills", response_model=list[SkillRead])
def list_skills(q: Optional[str] = None, db: Session = Depends(get_db)):
    stmt = select(Skill)
    if q:
        stmt = stmt.where(Skill.name.ilike(f"%{q}%"))
    stmt = stmt.order_by(Skill.name.asc())
    return list(db.execute(stmt).scalars().all())


@app.get("/skills/{skill_id}", response_model=SkillRead)
def get_skill(skill_id: int, db: Session = Depends(get_db)):
    skill = db.get(Skill, skill_id)
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    return skill


@app.get("/skills/jobs", response_model=list[SkillJobRead])
def list_jobs_for_skill(
    skill: Optional[str] = None,
    skill_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    if skill_id is None and (skill is None or not skill.strip()):
        raise HTTPException(status_code=422, detail="Provide either skill_id or skill name")

    if skill_id is not None:
        skill_obj = db.get(Skill, skill_id)
    else:
        skill_name = skill.strip()
        skill_obj = db.execute(
            select(Skill).where(Skill.name.ilike(skill_name))
        ).scalar_one_or_none()

    if not skill_obj:
        raise HTTPException(status_code=404, detail="Skill not found")

    rows = db.execute(
        select(JobSkill, Job)
        .join(Job, Job.id == JobSkill.job_id)
        .where(JobSkill.skill_id == skill_obj.id)
        .order_by(Job.id.desc())
    ).all()

    return [{"job": job, "how_used": job_skill.how_used} for job_skill, job in rows]


@app.get("/jobs", response_model=list[JobRead])
def list_jobs(
    q: Optional[str] = None,
    skill: Optional[str] = None,
    skill_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    stmt = select(Job)

    if q:
        stmt = stmt.where(or_(Job.company.ilike(f"%{q}%"), Job.title.ilike(f"%{q}%")))

    if skill_id is not None or (skill is not None and skill.strip()):
        stmt = stmt.join(JobSkill, JobSkill.job_id == Job.id).join(Skill, Skill.id == JobSkill.skill_id)

        if skill_id is not None:
            stmt = stmt.where(Skill.id == skill_id)
        else:
            stmt = stmt.where(Skill.name == skill.strip())

        stmt = stmt.distinct()

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


@app.delete("/skills/{skill_id}", status_code=204)
def delete_skill(skill_id: int, db: Session = Depends(get_db)):
    skill = db.get(Skill, skill_id)
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")

    try:
        db.delete(skill)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Skill is in use by one or more jobs")

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
