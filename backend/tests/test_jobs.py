import os
import pytest

def test_create_job_and_get_by_id(client):
    # Create
    r = client.post("/jobs", json={"company": "ExampleCo", "title": "QA Engineer"})
    assert r.status_code == 201
    job = r.json()
    assert job["id"] > 0
    assert job["company"] == "ExampleCo"
    assert job["title"] == "QA Engineer"
    print(r.json())

    job_id = job["id"]
    print(job_id)

    # Get by id
    r2 = client.get(f"/jobs/{job_id}")
    print(r2.status_code)
    assert r2.status_code == 200
    job2 = r2.json()
    assert job2["id"] == job_id
    assert job2["company"] == "ExampleCo"