import os
import pytest
import json

from sqlalchemy import text

from utils.strings import get_unique_s, create_field
from utils.api import create_complete_test_skill, post_create_skill

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