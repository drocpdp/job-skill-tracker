import os
import pytest
import json

from sqlalchemy import text

from utils.strings import get_unique_s, create_field
from utils.dates import make_date

from utils.api import create_new_job, post_create_job

def test_create_new_job(client):
    t_company = create_field("company")
    t_title = create_field("title")
    create_new_job(client, t_company=t_company, t_title=t_title)


def test_create_job_and_get_by_id(client):
    t_company = create_field("company")
    t_title = create_field("title")
    job = create_new_job(client, t_company=t_company, t_title=t_title)

    job_id = job["id"]
    job_company = job["company"]

    # Get by id
    r2 = client.get(f"/jobs/{job_id}")
    assert r2.status_code == 200
    job2 = r2.json()
    assert job2["id"] == job_id
    assert job2["company"] == job_company


def test_create_job_validate_all_fields_of_return_object(client):
    payload = {
        "t_company": create_field("company"),
        "t_title": create_field("title"),
        "t_location": create_field("location"),
        "t_start_date": make_date(year=2022, month=5, day=23),
        "t_end_date": make_date(year=2022, month=6, day=25),
        "t_summary": create_field("summary"),
        "t_notes": create_field("notes"),
    }

    create_new_job(
        client, **payload
    )


def test_create_job_missing_title(client):
    t_company = create_field("company")
    r = post_create_job(client, t_company=t_company)
    assert r.status_code == 422
    content_detail = json.loads(r.content)["detail"][0]["msg"]
    assert content_detail == "Field required"


def test_create_job_missing_company(client):
    t_title = create_field("title")
    r = post_create_job(client, t_title=t_title)
    assert r.status_code == 422
    content_detail = json.loads(r.content)["detail"][0]["msg"]
    assert content_detail == "Field required"


def test_create_job_missing_title_and_company(client):
    t_location = create_field("location")
    r = post_create_job(client, t_location=t_location)
    assert r.status_code == 422
    content_detail = json.loads(r.content)["detail"][0]["msg"]
    assert content_detail == "Field required"