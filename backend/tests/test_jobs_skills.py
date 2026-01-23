import os
import pytest
import json

from sqlalchemy import text

from utils.strings import get_unique_s, create_field
from utils.dates import make_date

from utils.api import create_new_job, post_create_job, create_complete_test_job, create_complete_test_skill

def test_add_skill_to_job(client):
    # Create job
    job_obj = create_complete_test_job(client)
    job_id = job_obj["id"]

    # Create skill - 1
    
    skill1 = create_complete_test_skill(client)
    skill1_id = skill1["id"]
    t_used_in1 = create_field("used-in-1")
    t_skill1 = skill1["name"]

    package = {
        "skill_id": skill1_id,
        "how_used": t_used_in1,
    }

    # Add skill to job

    r = client.post(f"/jobs/{job_id}/skills", json=package)
    assert r.status_code == 201    

    # validate

    r = client.get(f"/jobs/{job_id}/skills")
    r_json = r.json()
    assert r.status_code == 200

    rows = r.json()
    assert len(rows) == 1

    # re-shape to allow finding despite order
    by_id = {row["skill"]["id"]: row for row in rows}

    # name
    assert by_id[skill1_id]["skill"]["name"] == t_skill1
    # id
    assert skill1_id in by_id
    # used in
    assert by_id[skill1_id]["how_used"] == t_used_in1


def test_add_two_skills_to_job(client):
    # Create job
    job_obj = create_complete_test_job(client)
    job_id = job_obj["id"]

    # Create skill - 1
    
    skill1 = create_complete_test_skill(client)
    skill1_id = skill1["id"]
    t_used_in1 = create_field("used-in-1")
    t_skill1 = skill1["name"]

    package = {
        "skill_id": skill1_id,
        "how_used": t_used_in1,
    }

    # Add skill to job

    r = client.post(f"/jobs/{job_id}/skills", json=package)
    assert r.status_code == 201

    # Create skill - 2

    skill2 = create_complete_test_skill(client)
    skill2_id = skill2["id"]
    t_used_in2 = create_field("used-in-2")
    t_skill2 = skill2["name"]

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

    rows = r.json()
    assert len(rows) == 2

    # re-shape to allow finding despite order
    by_id = {row["skill"]["id"]: row for row in rows}

    # name
    assert by_id[skill1_id]["skill"]["name"] == t_skill1
    assert by_id[skill2_id]["skill"]["name"] == t_skill2    
    # id
    assert skill1_id in by_id
    assert skill2_id in by_id
    # used in
    assert by_id[skill1_id]["how_used"] == t_used_in1
    assert by_id[skill2_id]["how_used"] == t_used_in2


def test_delete_skill_from_job(client):
    # Create job
    job_obj = create_complete_test_job(client)
    job_id = job_obj["id"]

    # Create skill - 1
    
    skill1 = create_complete_test_skill(client)
    skill1_id = skill1["id"]
    t_used_in1 = create_field("used-in-1")
    t_skill1 = skill1["name"]

    package = {
        "skill_id": skill1_id,
        "how_used": t_used_in1,
    }

    # Add skill to job

    r = client.post(f"/jobs/{job_id}/skills", json=package)
    assert r.status_code == 201    

    # validate

    r = client.get(f"/jobs/{job_id}/skills")
    r_json = r.json()
    assert r.status_code == 200

    rows = r.json()
    assert len(rows) == 1

    # re-shape to allow finding despite order
    by_id = {row["skill"]["id"]: row for row in rows}

    # name
    assert by_id[skill1_id]["skill"]["name"] == t_skill1
    # id
    assert skill1_id in by_id
    # used in
    assert by_id[skill1_id]["how_used"] == t_used_in1

    # delete

    r = client.delete(f"/jobs/{job_id}/skills/{skill1_id}")
    assert r.status_code == 204

    # validate deleted (should not appear)

    r = client.get(f"/jobs/{job_id}/skills")
    r_json = r.json()
    assert r.status_code == 200

    rows = r.json()
    assert len(rows) == 0


def test_add_two_skills_to_job_delete_one_skill(client):
    # Create job
    job_obj = create_complete_test_job(client)
    job_id = job_obj["id"]

    # Create skill - 1
    
    skill1 = create_complete_test_skill(client)
    skill1_id = skill1["id"]
    t_used_in1 = create_field("used-in-1")
    t_skill1 = skill1["name"]

    package = {
        "skill_id": skill1_id,
        "how_used": t_used_in1,
    }

    # Add skill to job

    r = client.post(f"/jobs/{job_id}/skills", json=package)
    assert r.status_code == 201

    # Create skill - 2

    skill2 = create_complete_test_skill(client)
    skill2_id = skill2["id"]
    t_used_in2 = create_field("used-in-2")
    t_skill2 = skill2["name"]

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

    rows = r.json()
    assert len(rows) == 2

    # re-shape to allow finding despite order
    by_id = {row["skill"]["id"]: row for row in rows}

    # name
    assert by_id[skill1_id]["skill"]["name"] == t_skill1
    assert by_id[skill2_id]["skill"]["name"] == t_skill2    
    # id
    assert skill1_id in by_id
    assert skill2_id in by_id
    # used in
    assert by_id[skill1_id]["how_used"] == t_used_in1
    assert by_id[skill2_id]["how_used"] == t_used_in2    

    # delete (skill1)

    r = client.delete(f"/jobs/{job_id}/skills/{skill1_id}")
    assert r.status_code == 204

    # validate only skill2

    r = client.get(f"/jobs/{job_id}/skills")
    r_json = r.json()
    assert r.status_code == 200

    rows = r.json()
    assert len(rows) == 1

    # re-shape to allow finding despite order
    by_id = {row["skill"]["id"]: row for row in rows}

    # name
    assert by_id[skill2_id]["skill"]["name"] == t_skill2    
    # id
    assert skill1_id not in by_id
    assert skill2_id in by_id
    # used in
    assert by_id[skill2_id]["how_used"] == t_used_in2        


def test_attach_skill_to_non_existent_job(client):
    # Create job
    job_obj = create_complete_test_job(client)
    job_id = job_obj["id"]

    non_existent_job_id = job_id + 1    

    # Create skill - 1
    
    skill1 = create_complete_test_skill(client)
    skill1_id = skill1["id"]
    t_used_in1 = create_field("used-in-1")
    t_skill1 = skill1["name"]

    package = {
        "skill_id": skill1_id,
        "how_used": t_used_in1,
    }

    # Add skill to job, expect error

    r = client.post(f"/jobs/{non_existent_job_id}/skills", json=package)
    assert r.status_code == 404
    content_detail = json.loads(r.content)["detail"]
    assert content_detail == "Job not found"


def test_attach_duplicate_skill_to_job(client):
    # Create job
    job_obj = create_complete_test_job(client)
    job_id = job_obj["id"]

    # Create skill - 1
    
    skill1 = create_complete_test_skill(client)
    skill1_id = skill1["id"]
    t_used_in1 = create_field("used-in-1")
    t_skill1 = skill1["name"]

    package = {
        "skill_id": skill1_id,
        "how_used": t_used_in1,
    }

    # Add skill to job

    r = client.post(f"/jobs/{job_id}/skills", json=package)
    assert r.status_code == 201    

    # Create skill - duplicate
    #skill1 = create_complete_test_skill(client)
    skill1_id = skill1["id"]
    t_used_in1 = create_field("used-in-1")
    t_skill1 = skill1["name"]

    package = {
        "skill_id": skill1_id,
        "how_used": t_used_in1,
    }

    # Add skill to job

    r = client.post(f"/jobs/{job_id}/skills", json=package)
    assert r.status_code == 201    

    # validate

    r = client.get(f"/jobs/{job_id}/skills")
    r_json = r.json()
    assert r.status_code == 200

    rows = r.json()
    assert len(rows) == 1

    # re-shape to allow finding despite order
    by_id = {row["skill"]["id"]: row for row in rows}

    # name
    assert by_id[skill1_id]["skill"]["name"] == t_skill1
    #assert by_id[skill2_id]["skill"]["name"] == t_skill2    
    # id
    assert skill1_id in by_id
    #assert skill2_id in by_id
    # used in
    assert by_id[skill1_id]["how_used"] == t_used_in1
    #assert by_id[skill2_id]["how_used"] == t_used_in2    

