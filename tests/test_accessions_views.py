from random import randint

from .fixtures import *


def test_accessions_list(client, auth_header, org, accession):
    resp = client.get(f"/v1/orgs/{org.id}/accessions", headers=auth_header)
    assert resp.status_code == 200, resp.content
    accessions_json = resp.json()
    assert accessions_json[0]["id"] == accession.id
    assert accessions_json[0]["code"] == accession.code
    assert accessions_json[0]["taxon_id"] == accession.taxon_id


def test_accessions_create(client, auth_header, make_token, org, taxon):
    data = {"code": make_token(), "taxon_id": taxon.id}
    resp = client.post(f"/v1/orgs/{org.id}/accessions", headers=auth_header, json=data)
    assert resp.status_code == 201, resp.text
    accession_json = resp.json()
    assert isinstance(accession_json["id"], int)
    assert accession_json["code"] == data["code"]
    assert accession_json["taxon_id"] == data["taxon_id"]


def test_accession_detail(client, auth_header, org, accession):
    resp = client.get(
        f"/v1/orgs/{org.id}/accessions/{accession.id}", headers=auth_header
    )
    assert resp.status_code == 200, resp.text
    accession_json = resp.json()
    assert accession_json["id"] == accession.id
    assert accession_json["code"] == accession.code
    assert accession_json["taxon_id"] == accession.taxon_id


def test_accession_detail_missing(client, auth_header, org, accession):
    other_accession_id = randint(1, 100)
    resp = client.get(f"/v1/orgs/{org.id}/{other_accession_id}", headers=auth_header)
    assert resp.status_code == 404
