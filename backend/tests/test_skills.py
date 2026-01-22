import os
import pytest
import json

from sqlalchemy import text

from utils.strings import get_unique_s
from utils.api import create_complete_test_skill

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
