from .fixtures import *  # noqa: F401,F403


def test_profile_create(client, auth_header, current_user_id, org, faker):
    data = {"username": faker.simple_profile()["username"], "email": faker.email()}
    resp = client.post("/v1/profile", headers=auth_header, json=data)
    assert resp.status_code == 201, resp.content
    profile_json = resp.json()
    assert profile_json["user_id"] == current_user_id
    assert "id" not in profile_json, profile_json


def test_profile_create_fails_if_exists(client, auth_header, profile, faker):
    data = {"username": faker.simple_profile()["username"], "email": faker.email()}
    resp = client.post("/v1/profile", headers=auth_header, json=data)
    assert resp.status_code == 409, resp.content


def test_profile_detail(client, auth_header, current_user_id, profile):
    resp = client.get("/v1/profile", headers=auth_header)
    assert resp.status_code == 200
    profile_json = resp.json()
    assert profile_json["user_id"] == current_user_id
    assert "id" not in profile_json


def test_profile_update(client, auth_header, current_user_id, profile, faker):
    data = {"given_name": faker.first_name()}
    resp = client.patch("/v1/profile", headers=auth_header, json=data)
    assert resp.status_code == 200, resp.content
    profile_json = resp.json()
    assert "id" not in profile_json
    assert profile_json["user_id"] == current_user_id
    assert profile_json["given_name"] == data["given_name"]
