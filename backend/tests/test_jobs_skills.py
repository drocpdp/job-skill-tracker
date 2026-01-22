import os
import pytest
import json

from sqlalchemy import text

from utils.strings import get_unique_s
from utils.dates import make_date

from utils.api import create_new_job, post_create_job, create_complete_test_job


def test_add_two_skills_to_job(client):
    # Create job
    job_obj = create_complete_test_job(client)
    job_id = job_obj["id"]

    # Create skill - 1

    t_skill1 = "skill1-" + get_unique_s()
    r = client.post("/skills", json={"name": t_skill1})
    assert r.status_code == 201
    skill1 = r.json()
    skill1_id = skill1["id"]
    t_used_in1 = "used-in-1-" + get_unique_s()

    package = {
        "skill_id": skill1_id,
        "how_used": t_used_in1,
    }

    # Add skill to job

    r = client.post(f"/jobs/{job_id}/skills", json=package)
    assert r.status_code == 201


    # Create skill - 2

    t_skill2 = "skill2-" + get_unique_s()
    r = client.post("/skills", json={"name": t_skill2})
    assert r.status_code == 201
    skill2 = r.json()
    skill2_id = skill2["id"]
    t_used_in2 = "used-in-2-" + get_unique_s()

    package = {
        "skill_id": skill2_id,
        "how_used": t_used_in2,
        }

    # Add skill to job

    r = client.post(f"/jobs/{job_id}/skills", json=package)
    assert r.status_code == 201

    # validate

    r = client.get(f"/jobs/{job_id}/skills")
    r_json = r.json()
    assert r.status_code == 200
    skill1_r, skill2_r = r_json
    # name
    assert skill1_r["skill"]["name"] == t_skill1
    assert skill2_r["skill"]["name"] == t_skill2
    # id
    assert skill1_r["skill"]["id"] == skill1_id
    assert skill2_r["skill"]["id"] == skill2_id
    # used in
    assert skill1_r["how_used"] == t_used_in1
    assert skill2_r["how_used"] == t_used_in2   