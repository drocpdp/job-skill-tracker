# app/models.py
from typing import Optional
from sqlmodel import SQLModel, Field

class Skill(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    slug: str
    description: str
    url: Optional[str] = None

class Experience(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    slug: str
    description: str
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    url: Optional[str] = None

class Project(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    slug: str
    description: str
    url: Optional[str] = None

class Application(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    slug: str
    description: str
    url: Optional[str] = None