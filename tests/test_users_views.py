import pytest

from .fixtures import *


def test_users_detail(client, user):
    resp = client.get(f"/users/{user.id}")
    resp_json = resp.json()
    assert resp_json["id"] == user.id
    assert resp_json["username"] == user.username
    assert resp.status_code == 200, resp.json()
