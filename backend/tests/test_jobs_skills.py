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
    assert r.status_code == 409    
    r_json = r.json()
    assert r_json["detail"] == "Skill already attached to this job"


def test_add_one_skill_to_two_different_jobs_validate_added_to_both_jobs(client):
    # Create job 1
    job_obj1 = create_complete_test_job(client)
    job_id1 = job_obj1["id"] 

    # Create job 2
    job_obj2 = create_complete_test_job(client)
    job_id2 = job_obj2["id"]    

    # Create skill
    skill = create_complete_test_skill(client)
    skill_id = skill["id"]
    skill_name = skill["name"]

    # Link skill to job 1
    r = client.post(f"/jobs/{job_id1}/skills", json={"skill_id": skill_id})
    assert r.status_code == 201

    # Link skill to job 2
    r = client.post(f"/jobs/{job_id2}/skills", json={"skill_id": skill_id})
    assert r.status_code == 201

    # validation data object (re-form data)
    skills_by_job_id = {}

    # Job 1 added to validation object
    r = client.get(f"/jobs/{job_id1}/skills")
    r_json = r.json()
    skills_by_job_id[job_id1] = r_json
    assert r.status_code == 200

    # Job 2 added to validation object
    r = client.get(f"/jobs/{job_id2}/skills")
    r_json = r.json()
    skills_by_job_id[job_id2] = r_json
    assert r.status_code == 200

    # Validate skill added to Job 1
    assert skills_by_job_id[job_id1][0]["skill"]["id"] == skill_id
    assert skills_by_job_id[job_id1][0]["skill"]["name"] == skill_name

    # Validate skill added to Job 2
    assert skills_by_job_id[job_id2][0]["skill"]["id"] == skill_id
    assert skills_by_job_id[job_id2][0]["skill"]["name"] == skill_name    


def test_add_one_skill_to_two_different_jobs_delete_one_skill_to_job_relation_validate_other_relation_unaffected(client):
    # Create job 1
    job_obj1 = create_complete_test_job(client)
    job_id1 = job_obj1["id"] 

    # Create job 2
    job_obj2 = create_complete_test_job(client)
    job_id2 = job_obj2["id"]    

    # Create skill
    skill = create_complete_test_skill(client)
    skill_id = skill["id"]
    skill_name = skill["name"]

    # Link skill to job 1
    r = client.post(f"/jobs/{job_id1}/skills", json={"skill_id": skill_id})
    assert r.status_code == 201

    # Link skill to job 2
    r = client.post(f"/jobs/{job_id2}/skills", json={"skill_id": skill_id})
    assert r.status_code == 201    

    # Delete link skill to job 1
    r = client.delete(f"/jobs/{job_id1}/skills/{skill_id}")
    assert r.status_code == 204, r.text

    # validation data object (re-form data)
    skills_by_job_id = {}

    # Job 1 skills link GET
    r = client.get(f"/jobs/{job_id1}/skills")
    r_json = r.json()
    skills_by_job_id[job_id1] = r_json
    assert r.status_code == 200

    # Job 2 skills link GET
    r = client.get(f"/jobs/{job_id2}/skills")
    r_json = r.json()
    skills_by_job_id[job_id2] = r_json
    assert r.status_code == 200
    
    assert job_id1 in skills_by_job_id
    assert job_id2 in skills_by_job_id
    
    # Validate skill association deleted from Job 1
    assert skills_by_job_id[job_id1] == []
    
    # Validate skill association NOT deleted from Job 2
    assert skills_by_job_id[job_id2][0]["skill"]["id"] == skill_id
    assert skills_by_job_id[job_id2][0]["skill"]["name"] == skill_name        


def test_delete_skill_in_use_fails(client):
    # Create job
    job = create_complete_test_job(client)
    job_id = job["id"]

    # Create skill
    skill = create_complete_test_skill(client)
    skill_id = skill["id"]
    skill_name = skill["name"]

    # Attach skill to job
    r = client.post(
        f"/jobs/{job_id}/skills",
        json={"skill_id": skill_id, "how_used": "Primary backend DB"},
    )
    assert r.status_code == 201

    # Attempt to delete skill
    r = client.delete(f"/skills/{skill_id}")

    # This is the key assertion
    assert r.status_code == 409
    assert "in use" in r.json()["detail"].lower()

    # assert skill not deleted

    # validation data object (re-form data)
    skills_by_job_id = {}

    # Job 1 skills link GET
    r = client.get(f"/jobs/{job_id}/skills")
    r_json = r.json()
    skills_by_job_id[job_id] = r_json
    assert r.status_code == 200
    
    assert job_id in skills_by_job_id
    
    # Validate skill association NOT deleted from Job
    assert skills_by_job_id[job_id][0]["skill"]["id"] == skill_id
    assert skills_by_job_id[job_id][0]["skill"]["name"] == skill_name        

