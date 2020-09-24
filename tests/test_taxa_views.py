from random import randint

from .fixtures import *


def test_taxa_list(client, auth_header, org, taxon):
    resp = client.get(f"/v1/orgs/{org.id}/taxa", headers=auth_header)
    assert resp.status_code == 200, resp.content
    taxa_json = resp.json()
    assert taxa_json[0]["id"] == taxon.id
    assert taxa_json[0]["name"] == taxon.name


def test_create(client, auth_header, make_token, org):
    data = {"name": make_token(), "rank": "family"}
    resp = client.post(f"/v1/orgs/{org.id}/taxa", headers=auth_header, json=data)
    assert resp.status_code == 201
    taxon_json = resp.json()
    assert isinstance(taxon_json["id"], int)
    assert taxon_json["name"] == data["name"]
    assert taxon_json["rank"] == data["rank"]


def test_taxon_detail(client, auth_header, org, taxon):
    resp = client.get(f"/v1/orgs/{org.id}/taxa/{taxon.id}", headers=auth_header)
    assert resp.status_code == 200
    taxon_json = resp.json()
    assert taxon_json["id"] == taxon.id
    assert taxon_json["name"] == taxon.name
    assert taxon_json["rank"] == taxon.rank


def test_taxon_detail_missing(client, auth_header, org, taxon):
    other_taxon_id = randint(1, 100)
    resp = client.get(f"/v1/orgs/{org.id}/{other_taxon_id}", headers=auth_header)
    assert resp.status_code == 404
