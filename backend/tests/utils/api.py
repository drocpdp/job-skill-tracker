import os
import pytest
import json

from utils.strings import get_unique_s
from utils.dates import make_date

def create_job_json(t_company=None, t_title=None, t_location=None, t_start_date=None, t_end_date=None, t_summary=None, t_notes=None ):
    """
    Create json payload of create job.
    """

    job_payload = {}

    if t_company is None:
        t_company = "company-" + get_unique_s()
    job_payload["company"] = t_company
    
    if t_title is None:
        t_title = "title-" + get_unique_s()
    job_payload["title"] = t_title
    
    if t_location is None:
        t_location = "location-" + get_unique_s()
    job_payload["location"] = t_location
    
    if t_start_date is None:
        t_start_date = make_date(year=2020, month=5, day=23)
    job_payload["start_date"] = t_start_date
    
    if t_end_date is None:
        t_end_date = make_date(year=2022, month=1, day=10)
    job_payload["end_date"] = t_end_date
    
    if t_summary is None:
        t_summary = "summary-" + get_unique_s()
    job_payload["summary"] = t_summary
    
    if t_notes is None:
        t_notes = "notes-" + get_unique_s()
    job_payload["notes"] = t_notes
    
    return job_payload


def create_new_job(client, t_company=None, t_title=None, t_location=None, t_start_date=None, t_end_date=None, t_summary=None, t_notes=None):
    """
    Create new job, and validate the RESPONSE object fields == payload fields
    """

    job_payload = create_job_json(t_company, t_title, t_location, t_start_date, t_end_date, t_summary, t_notes)
    
    # Create
    r = client.post("/jobs", json=job_payload)
    assert r.status_code == 201
    job = r.json()
    assert job["id"] > 0
    assert job["company"] == job_payload["company"]
    assert job["title"] == job_payload["title"]

    if t_location:
        assert job["location"] == job_payload["location"]
    if t_start_date:
        assert job["start_date"] == job_payload["start_date"]
    if t_end_date:
        assert job["end_date"] == job_payload["end_date"]
    if t_summary:
        assert job["summary"] == job_payload["summary"]
    if t_notes:
        assert job["notes"] == job_payload["notes"]

    return job


