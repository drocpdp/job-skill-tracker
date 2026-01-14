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