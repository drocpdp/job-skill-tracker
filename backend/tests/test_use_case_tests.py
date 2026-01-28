import os
import pytest
import json

from sqlalchemy import text

from utils.strings import get_unique_s, create_field
from utils.dates import make_date

from utils.api import create_new_job, post_create_job, create_complete_test_job, get_sample_job_payload


def test_create_job_and_edit_date_of_job(client):
    # create job
    job = create_complete_test_job(client)
    
    job_fields = {k:v for k, v in job.items()}

    job_id = job_fields["id"]

    # validate
    r = client.get(f"/jobs/{job_id}")
    assert r.status_code == 200

    for k, v in r.json().items():
        assert k in job_fields
        assert job_fields[k] == v
    
    # change start date of job
    new_start_date = make_date(year=2000, month=12, day=12)
    job_fields["start_date"] = new_start_date
    payload = {"start_date": new_start_date}
    r = client.patch(f"/jobs/{job_id}", json=payload)
    assert r.status_code == 200

    # validate
    r = client.get(f"/jobs/{job_id}")
    assert r.status_code == 200

    for k, v in r.json().items():
        assert k in job_fields
        assert job_fields[k] == v


    # change end date of job
    new_start_date = make_date(year=2030, month=1, day=23)
    job_fields["start_date"] = new_start_date
    payload = {"start_date": new_start_date}
    r = client.patch(f"/jobs/{job_id}", json=payload)
    assert r.status_code == 200

    # validate
    r = client.get(f"/jobs/{job_id}")
    assert r.status_code == 200

    for k, v in r.json().items():
        assert k in job_fields
        assert job_fields[k] == v
