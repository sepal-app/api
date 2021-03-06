from random import randint

from sepal.organizations.models import RoleType

from .factories import OrganizationFactory
from .fixtures import *  # noqa: F401,F403


def test_org_create(client, auth_header, make_token, current_user_id):
    data = {"name": make_token()}
    resp = client.post("/v1/orgs", headers=auth_header, json=data)
    assert resp.status_code == 201, resp.content
    org_json = resp.json()
    assert org_json["name"] == data["name"]


def test_org_list(client, auth_header, org):
    resp = client.get("/v1/orgs", headers=auth_header)
    assert resp.status_code == 200, resp.content
    orgs_json = resp.json()
    assert orgs_json[0]["id"] == org.id
    assert orgs_json[0]["name"] == org.name


def test_org_detail(client, auth_header, org):
    resp = client.get(f"/v1/orgs/{org.id}", headers=auth_header)
    assert resp.status_code == 200
    org_json = resp.json()
    assert org_json["id"] == org.id
    assert org_json["name"] == org.name


def test_org_detail_missing(client, auth_header, org):
    other_org_id = randint(1, 100)
    resp = client.get(f"/v1/orgs/{other_org_id}", headers=auth_header)
    assert resp.status_code == 404


def test_org_detail_not_authorized(client, session, current_user_id, auth_header):
    org = OrganizationFactory()  # user is not a member of this org
    session.add(org)
    session.commit()
    resp = client.get(f"/v1/orgs/{org.id}", headers=auth_header)
    assert resp.status_code == 404


def test_org_users_list(client, session, current_user_id, profile, org, auth_header):
    resp = client.get(f"/v1/orgs/{org.id}/users", headers=auth_header)
    assert resp.status_code == 200
    users_json = resp.json()
    assert users_json[0]["profile"]["user_id"] == current_user_id
    assert users_json[0]["role"] == RoleType.Owner.value
