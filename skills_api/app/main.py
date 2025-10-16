#app/main.py
from fastapi import FastAPI, Depends, HTTPException
from typing import List
from sqlmodel import Session, select
from app.database import create_db_and_tables, get_session
from app.models import Skill

app = FastAPI(title="Skills API", version="0.0.1")

@app.on_event("startup")
def on_startup():
    create_db_and_tables()
