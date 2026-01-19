import os
import pytest
import json

from sqlalchemy import text

from utils.strings import get_unique_s

def test_create_skill_and_get_by_id(client):
    t_skill = "skill-" + get_unique_s()
    # Create
    r = client.post("/skills", json={"name": t_skill})
    assert r.status_code == 201
    skill = r.json()
    assert skill["id"] > 0
    assert skill["name"] == t_skill

    skill_id = skill["id"]

    # Get by id
    r_get = client.get(f"/skills/{skill_id}")
    assert r_get.status_code == 200
    skill_get = r_get.json()
    assert skill_get["id"] == skill_id
    assert skill_get["name"] == t_skill
