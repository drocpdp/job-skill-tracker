import os
import pytest
import json

from sqlalchemy import text

from utils.strings import get_unique_s
from utils.dates import make_date

from utils.api import create_new_job

def test_create_new_job(client):
    create_new_job(client)


def test_create_job_and_get_by_id(client):
    job = create_new_job(client)

    job_id = job["id"]
    job_company = job["company"]

    # Get by id
    r2 = client.get(f"/jobs/{job_id}")
    assert r2.status_code == 200
    job2 = r2.json()
    assert job2["id"] == job_id
    assert job2["company"] == job_company

def test_create_job_validate_all_fields_of_return_object(client):
    t_company = "company-" + get_unique_s()
    t_title = "title-" + get_unique_s()
    t_location = "location-" + get_unique_s()
    t_start_date = make_date(year=2022, month=5, day=23)
    t_end_date = make_date(year=2022, month=6, day=25)
    t_summary = "summary-" + get_unique_s()
    t_notes = "notes-" + get_unique_s()

    create_new_job(
        client, 
        t_company=t_company,
        t_title=t_title, 
        t_location=t_location, 
        t_start_date=t_start_date, 
        t_end_date=t_end_date,
        t_summary=t_summary,
        t_notes=t_notes
    )

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