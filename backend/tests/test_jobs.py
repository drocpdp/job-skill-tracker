import os
import pytest
import json

from sqlalchemy import text

from utils.strings import get_unique_s, create_field
from utils.dates import make_date

from utils.api import create_new_job, post_create_job, create_complete_test_job


def test_create_new_job(client):
    t_company = create_field("company")
    t_title = create_field("title")
    job = create_new_job(client, t_company=t_company, t_title=t_title)

    job_id = job["id"]
    job_company = job["company"]

    #validate
    r2 = client.get(f"/jobs/{job_id}")
    assert r2.status_code == 200
    job2 = r2.json()
    assert job2["id"] == job_id
    assert job2["company"] == job_company    


def test_create_new_job_with_duplicate_company_name_and_title(client):
    """ 
    For now, creates separate jobs
    """
    t_company = create_field("company")
    t_title = create_field("title")

    #DUPLICATE
    job = create_new_job(client, t_company=t_company, t_title=t_title)
    job2 = create_new_job(client, t_company=t_company, t_title=t_title)

    job_id = job["id"]
    job_company = job["company"]

    # Get by id
    r2 = client.get(f"/jobs/{job_id}")
    assert r2.status_code == 200
    job2 = r2.json()
    assert job2["id"] == job_id
    assert job2["company"] == job_company

    job_id = job2["id"]
    job_company = job2["company"]

    # Get by id (duplicate)
    r2 = client.get(f"/jobs/{job_id}")
    assert r2.status_code == 200
    job2 = r2.json()
    assert job2["id"] == job_id
    assert job2["company"] == job_company    
    

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

    job = create_new_job(
        client, **payload
    )

    job_id = job["id"]

    # Get by id
    r2 = client.get(f"/jobs/{job_id}")
    assert r2.status_code == 200
    job2 = r2.json()
    # payload == t_*, response == *
    for k in payload:
        resp_k = k[2:]
        assert job2[resp_k] == payload[k]


def test_create_job_validate_all_fields_of_return_object_missing_location(client):
    payload = {
        "t_company": create_field("company"),
        "t_title": create_field("title"),
        #"t_location": create_field("location"),
        "t_start_date": make_date(year=2022, month=5, day=23),
        "t_end_date": make_date(year=2022, month=6, day=25),
        "t_summary": create_field("summary"),
        "t_notes": create_field("notes"),
    }

    job = create_new_job(
        client, **payload
    )

    job_id = job["id"]

    # Get by id
    r2 = client.get(f"/jobs/{job_id}")
    assert r2.status_code == 200
    job2 = r2.json()
    # payload == t_*, response == *
    for k in payload:
        resp_k = k[2:]
        assert job2[resp_k] == payload[k]        


def test_create_job_validate_all_fields_of_return_object_missing_summary(client):
    payload = {
        "t_company": create_field("company"),
        "t_title": create_field("title"),
        "t_location": create_field("location"),
        "t_start_date": make_date(year=2022, month=5, day=23),
        "t_end_date": make_date(year=2022, month=6, day=25),
        #"t_summary": create_field("summary"),
        "t_notes": create_field("notes"),
    }

    job = create_new_job(
        client, **payload
    )

    job_id = job["id"]

    # Get by id
    r2 = client.get(f"/jobs/{job_id}")
    assert r2.status_code == 200
    job2 = r2.json()
    # payload == t_*, response == *
    for k in payload:
        resp_k = k[2:]
        assert job2[resp_k] == payload[k]               


def test_create_job_validate_all_fields_of_return_object_missing_notes(client):
    payload = {
        "t_company": create_field("company"),
        "t_title": create_field("title"),
        "t_location": create_field("location"),
        "t_start_date": make_date(year=2022, month=5, day=23),
        "t_end_date": make_date(year=2022, month=6, day=25),
        "t_summary": create_field("summary"),
        #"t_notes": create_field("notes"),
    }

    job = create_new_job(
        client, **payload
    )

    job_id = job["id"]

    # Get by id
    r2 = client.get(f"/jobs/{job_id}")
    assert r2.status_code == 200
    job2 = r2.json()
    # payload == t_*, response == *
    for k in payload:
        resp_k = k[2:]
        assert job2[resp_k] == payload[k]               


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


def test_get_jobs_validate_returned_list_of_all_jobs(client):
    jobs = {}

    num_tests = 4

    for _ in range(num_tests):
        job = create_complete_test_job(client)
        job_id = job["id"]
        company_name = job["company"]

        jobs["id"] = [company_name, job]

    # Get all jobs
    r_get = client.get(f"/jobs/")
    assert r_get.status_code == 200

    jobs_get = r_get.json()

    assert len(jobs_get) == num_tests

    jobs_by_company_names = {job["company"]: job for job in jobs_get}

    unique_job_company_names = {company_name for company_name in jobs_by_company_names}

    assert len(unique_job_company_names) == num_tests


def test_get_jobs_with_similar_company_name_string_expect_set_of_results(client):
    jobs = {}

    num_tests = 4

    common_string = "compa" # all jobs have 'company' within

    for _ in range(num_tests):
        job = create_complete_test_job(client)
        job_id = job["id"]
        job_company_name = job["company"]

        jobs[job_id] = [job_company_name, job]

    # Get by common name
    r_get = client.get(f"/jobs/", params={"q":common_string})
    assert r_get.status_code == 200

    job_get = r_get.json()

    assert len(job_get) == num_tests

    jobs_by_company_names = {job["company"]: job for job in job_get}

    for name in jobs_by_company_names:
        assert common_string in name


def test_get_jobs_with_non_existent_company_name_expect_no_results(client):
    jobs = {}

    num_tests = 4

    common_string = "XXX"

    for _ in range(num_tests):
        job = create_complete_test_job(client)
        job_id = job["id"]
        job_company_name = job["company"]

        jobs[job_id] = [job_company_name, job]

    # Get by common name
    r_get = client.get(f"/jobs/", params={"q":common_string})
    assert r_get.status_code == 200

    job_get = r_get.json()

    assert len(job_get) == 0