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

