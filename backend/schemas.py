from datetime import date
from typing import Optional

from pydantic import BaseModel, ConfigDict

class JobCreate(BaseModel):
    company: str
    title: str
    location: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    summary: Optional[str] = None
    notes: Optional[str] = None

class JobRead(JobCreate):
    id: int
    model_config = ConfigDict(from_attributes=True)

class JobUpdate(BaseModel):
    company: Optional[str] = None
    title: Optional[str] = None
    location: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    summary: Optional[str] = None
    notes: Optional[str] = None

class SkillCreate(BaseModel):
    name: str
    category: Optional[str] = None
    notes: Optional[str] = None

class SkillRead(SkillCreate):
    id: int
    model_config = ConfigDict(from_attributes=True)

class JobSkillUpsert(BaseModel):
    """
    Payload to attach a skill to a job.
    - If skill_id is provided, we attach that existing skill.
    - Otherwise we create/find by skill.name.
    """
    skill_id: Optional[int] = None
    skill: Optional[SkillCreate] = None
    how_used: Optional[str] = None

class JobSkillRead(BaseModel):
    skill: SkillRead
    how_used: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)
