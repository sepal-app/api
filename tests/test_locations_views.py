from random import randint

from .fixtures import *  # noqa: F401,F403


def test_locations_list(client, auth_header, org, location):
    resp = client.get(f"/v1/orgs/{org.id}/locations", headers=auth_header)
    assert resp.status_code == 200, resp.content
    locations_json = resp.json()
    assert locations_json[0]["id"] == location.id
    assert locations_json[0]["name"] == location.name


def test_locations_create(client, auth_header, make_token, org):
    data = {"name": make_token(), "code": make_token()}
    resp = client.post(f"/v1/orgs/{org.id}/locations", headers=auth_header, json=data)
    assert resp.status_code == 201, resp.text
    location_json = resp.json()
    assert isinstance(location_json["id"], int)
    assert location_json["name"] == data["name"]
    assert location_json["code"] == data["code"]


def test_location_detail(client, auth_header, org, location):
    resp = client.get(f"/v1/orgs/{org.id}/locations/{location.id}", headers=auth_header)
    assert resp.status_code == 200, resp.text
    location_json = resp.json()
    assert location_json["id"] == location.id
    assert location_json["name"] == location.name
    assert location_json["code"] == location.code


def test_location_detail_missing(client, auth_header, org, location):
    other_location_id = randint(1, 100)
    resp = client.get(f"/v1/orgs/{org.id}/{other_location_id}", headers=auth_header)
    assert resp.status_code == 404
