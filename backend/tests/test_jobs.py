import os
import pytest
import json

from sqlalchemy import text

from utils.strings import get_unique_s
from utils.dates import make_date

def test_create_job_and_get_by_id(client):
    t_company = "company-" + get_unique_s()
    t_title = "title-" + get_unique_s()
    # Create
    r = client.post("/jobs", json={"company": t_company, "title": t_title})
    assert r.status_code == 201
    job = r.json()
    assert job["id"] > 0
    assert job["company"] == t_company
    assert job["title"] == t_title

    job_id = job["id"]

    # Get by id
    r2 = client.get(f"/jobs/{job_id}")
    assert r2.status_code == 200
    job2 = r2.json()
    assert job2["id"] == job_id
    assert job2["company"] == t_company

def test_create_job_validate_all_fields(client):
    t_company = "company-" + get_unique_s()
    t_title = "title-" + get_unique_s()
    t_location = "location-" + get_unique_s()
    t_start_date = make_date(year=2022, month=5, day=23)
    t_end_date = make_date(year=2022, month=6, day=25)
    t_summary = "summary-" + get_unique_s()
    t_notes = "notes-" + get_unique_s()

    job_payload = {
        "company": t_company,
        "title": t_title,
        "location": t_location,
        "start_date": t_start_date,
        "end_date": t_end_date,
        "summary": t_summary,
        "notes": t_notes
    }

    r = client.post("/jobs", json=job_payload)
    assert r.status_code == 201
    job = r.json()
    assert job["company"] == t_company
    assert job["title"] == t_title
    assert job["location"] == t_location
    assert job["start_date"] == t_start_date
    assert job["end_date"] == t_end_date
    assert job["summary"] == t_summary
    assert job["notes"] == t_notes

def test_create_job_missing_title(client):
    t_company = "company-" + get_unique_s()
    r = client.post("/jobs", json={"company": t_company})
    assert r.status_code == 422
    content_detail = json.loads(r.content)["detail"][0]["msg"]
    assert content_detail == "Field required"

def test_create_job_missing_company(client):
    t_title = "title-" + get_unique_s()
    r = client.post("/jobs", json={"title": t_title})
    assert r.status_code == 422
    content_detail = json.loads(r.content)["detail"][0]["msg"]
    assert content_detail == "Field required"

def test_create_job_missing_title_and_company(client):
    t_location = "location-" + get_unique_s()
    r = client.post("/jobs", json={"location": t_location})
    assert r.status_code == 422
    content_detail = json.loads(r.content)["detail"][0]["msg"]
    assert content_detail == "Field required"