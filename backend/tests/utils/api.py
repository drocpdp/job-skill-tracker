import os
import pytest
import json

from utils.strings import get_unique_s, create_field
from utils.dates import make_date

def post_create_job(client, **kwargs):
    payload = {
        "company": kwargs.get("t_company"),
        "title": kwargs.get("t_title"),
        "location": kwargs.get("t_location"),
        "start_date": kwargs.get("t_start_date"),
        "end_date": kwargs.get("t_end_date"),
        "summary": kwargs.get("t_summary"),
        "notes": kwargs.get("t_notes"),
    }
    payload = {k: v for k, v in payload.items() if v is not None}

    return client.post("/jobs", json=payload)

def create_new_job(client, **kwargs):
    """
    Create new job, and validate the RESPONSE object fields == payload fields
    """
    
    # Create
    r = post_create_job(client, **kwargs)

    assert r.status_code == 201
    job = r.json()
    assert job["id"] > 0
    assert job["company"] == kwargs.get("t_company")
    assert job["title"] == kwargs.get("t_title")

    if "t_location" in kwargs:
        assert job["location"] == kwargs.get("t_location")
    if "t_start_date" in kwargs:
        assert job["start_date"] == kwargs.get("t_start_date")
    if "t_end_date" in kwargs:
        assert job["end_date"] == kwargs.get("t_end_date")
    if "t_summary" in kwargs:
        assert job["summary"] == kwargs.get("t_summary")
    if "t_notes" in kwargs:
        assert job["notes"] == kwargs.get("t_notes")

    return job


def create_complete_test_job(client):
    payload = {
        "t_company": create_field("company"),
        "t_title": create_field("title"),
        "t_location": create_field("location"),
        "t_start_date": make_date(year=2022, month=5, day=23),
        "t_end_date": make_date(year=2024, month=12, day=14),
        "t_summary": create_field("summary"),
        "t_notes": create_field("notes"),
    }
    return create_new_job(client, **payload)