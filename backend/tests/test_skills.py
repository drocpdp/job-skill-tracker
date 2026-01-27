import os
import pytest
import json

from sqlalchemy import text

from utils.strings import get_unique_s, create_field
from utils.api import create_complete_test_skill, post_create_skill, create_complete_test_job

def test_create_skill_and_get_by_id(client):
    skill = create_complete_test_skill(client)

    skill_id = skill["id"]
    skill_name = skill["name"]

    # Get by id
    r_get = client.get(f"/skills/{skill_id}")
    assert r_get.status_code == 200
    skill_get = r_get.json()
    assert skill_get["id"] == skill_id
    assert skill_get["name"] == skill_name


def test_create_skill_without_name_expect_error(client):
    payload = {
        "t_category": create_field("category"),
        "t_notes": create_field("notes"),
    }    
    skill = post_create_skill(client, **payload)
    assert skill.status_code == 422
    content_detail = json.loads(skill.content)["detail"][0]["msg"]
    assert content_detail == "Field required"


def test_create_skill_get_by_name(client):
    skill = create_complete_test_skill(client)

    skill_id = skill["id"]
    skill_name = skill["name"]

    # Get by name
    r_get = client.get(f"/skills/", params={"q":skill_name})
    assert r_get.status_code == 200
    skill_get = r_get.json()
    skills_by_names = {skill["name"]: skill for skill in skill_get}
    
    assert skill_name in skills_by_names

    assert skill_get[0]["id"] == skill_id
    assert skill_get[0]["name"] == skill_name


def test_create_skill_get_by_partial_name(client):
    skill = create_complete_test_skill(client)

    skill_id = skill["id"]
    skill_name = skill["name"]

    partial_skill_name = skill["name"][2:-2]

    # Get by name
    r_get = client.get(f"/skills/", params={"q":partial_skill_name})
    assert r_get.status_code == 200
    skill_get = r_get.json()
    skills_by_names = {skill["name"]: skill for skill in skill_get}
    
    assert skill_name in skills_by_names

    assert skill_get[0]["id"] == skill_id
    assert skill_get[0]["name"] == skill_name    


def test_get_skill_using_non_existent_id_expect_404(client):
    skill = create_complete_test_skill(client)

    skill_id = skill["id"]
    invalid_skill_id = skill_id + 1

    # Get by id
    r_get = client.get(f"/skills/{invalid_skill_id}")
    assert r_get.status_code == 404
    content_detail = r_get.json()["detail"]
    assert content_detail == "Skill not found"


def test_get_skill_using_non_existent_name_expect_empty_set(client):
    skill = create_complete_test_skill(client)

    skill_id = skill["id"]
    skill_name = skill["name"]
    invalid_skill_name = skill_name + "XXX"

    # Get by name
    r_get = client.get(f"/skills/", params={"q":invalid_skill_name})
    assert r_get.status_code == 200
    skill_get = r_get.json()
    skills_by_names = {skill["name"]: skill for skill in skill_get}
    
    assert len(skills_by_names) == 0


def test_get_skills_with_similar_name_string_expect_set_of_results(client):
    skills = {}

    num_tests = 4

    common_string = "na"

    for _ in range(num_tests):
        skill = create_complete_test_skill(client)
        skill_id = skill["id"]
        skill_name = skill["name"]

        skills[skill_id] = [skill_name, skill]

    # Get by common name
    r_get = client.get(f"/skills/", params={"q":common_string})
    assert r_get.status_code == 200

    skill_get = r_get.json()

    assert len(skill_get) == num_tests

    skills_by_names = {skill["name"]: skill for skill in skill_get}

    for name in skills_by_names:
        assert common_string in name


def test_get_skills_expect_set_of_results_to_match_number_of_entries(client):
    skills = {}

    num_tests = 4

    for _ in range(num_tests):
        skill = create_complete_test_skill(client)
        skill_id = skill["id"]
        skill_name = skill["name"]

        skills[skill_id] = [skill_name, skill]

    # Get by common name
    r_get = client.get(f"/skills/")
    assert r_get.status_code == 200

    skill_get = r_get.json()

    assert len(skill_get) == num_tests


def test_change_name_of_added_skill(client):
    # Create skill
    skill = create_complete_test_skill(client)
    skill_id = skill["id"]
    skill_name = skill["name"]
    skill_notes = skill["notes"]

    # Get by id
    r_get = client.get(f"/skills/{skill_id}")
    assert r_get.status_code == 200
    skill_get = r_get.json()
    assert skill_get["id"] == skill_id
    assert skill_get["name"] == skill_name
    assert skill_get["notes"] == skill_notes

    # Change name
    payload = {"name": create_field("UPDATE-NAME")}
    r = client.patch(f"/skills/{skill_id}", json=payload)
    r_json = r.json()
    assert r_json["name"] == payload["name"]

    r_get = client.get(f"/skills/{skill_id}")
    assert r_get.status_code == 200
    skill_get = r_get.json()
    assert skill_get["id"] == skill_id
    assert skill_get["name"] == payload["name"]
    assert skill_get["notes"] == skill_notes    


def test_change_notes_of_added_skill(client):
    # Create skill
    skill = create_complete_test_skill(client)
    skill_id = skill["id"]
    skill_name = skill["name"]
    skill_notes = skill["notes"]

    # Get by id
    r_get = client.get(f"/skills/{skill_id}")
    assert r_get.status_code == 200
    skill_get = r_get.json()
    assert skill_get["id"] == skill_id
    assert skill_get["name"] == skill_name
    assert skill_get["notes"] == skill_notes

    # Change notes
    payload = {"notes": create_field("UPDATE-NAME")}
    r = client.patch(f"/skills/{skill_id}", json=payload)
    assert r.status_code == 200
    r_json = r.json()
    assert r_json["notes"] == payload["notes"]    

    r_get = client.get(f"/skills/{skill_id}")
    assert r_get.status_code == 200
    skill_get = r_get.json()
    assert skill_get["id"] == skill_id
    assert skill_get["name"] == skill_name
    assert skill_get["notes"] == payload["notes"]


def test_change_notes_of_added_skill_to_duplicate_name_skill(client):
    # Create skill
    skill = create_complete_test_skill(client)
    skill_id = skill["id"]
    skill_name = skill["name"]
    skill_notes = skill["notes"]

    # Get by id
    r_get = client.get(f"/skills/{skill_id}")
    assert r_get.status_code == 200
    skill_get = r_get.json()
    assert skill_get["id"] == skill_id
    assert skill_get["name"] == skill_name
    assert skill_get["notes"] == skill_notes

    # Change name
    new_notes = create_field("NEW-NOTES")
    payload = {"name": skill_name, "notes": new_notes}
    r = client.patch(f"/skills/{skill_id}", json=payload)
    assert r.status_code == 200
    r_json = r.json()
    assert r_json["name"] == payload["name"]
    assert r_json["notes"] == payload["notes"]

    r_get = client.get(f"/skills/{skill_id}")
    assert r_get.status_code == 200
    skill_get = r_get.json()
    assert skill_get["id"] == skill_id
    assert skill_get["name"] == payload["name"]
    assert skill_get["notes"] == payload["notes"]


def test_delete_non_existent_skill(client):
    # Create job
    job = create_complete_test_job(client)
    job_id = job["id"]

    # Create skill
    skill = create_complete_test_skill(client)
    skill_id = skill["id"]
    skill_name = skill["name"]
    skill_notes = skill["notes"]

    # Get by id
    r_get = client.get(f"/skills/{skill_id}")
    assert r_get.status_code == 200
    skill_get = r_get.json()
    assert skill_get["id"] == skill_id
    assert skill_get["name"] == skill_name
    assert skill_get["notes"] == skill_notes

    # Attempt to delete skill
    r = client.delete(f"/skills/{skill_id}")

    assert r.status_code == 204

    r_get = client.get(f"/skills/{skill_id}")
    assert r_get.status_code == 404
    assert r_get.json()["detail"] == "Skill not found"


def test_create_duplicate_named_skill_expect_409_error(client):
    # create skill
    skill = create_complete_test_skill(client)
    skill_id = skill["id"]
    skill_name = skill["name"]
    skill_notes = skill["notes"]

    # create duplicate skill
    payload = {"t_name": skill_name}
    r_post = post_create_skill(client, **payload)
    assert r_post.status_code == 409
    assert r_post.json()["detail"] == "Skill already exists"
    