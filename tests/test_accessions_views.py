from random import randint
from urllib.parse import parse_qs, urlparse

from .fixtures import *  # noqa: F401,F403


def test_accessions_list(client, auth_header, org, accession):
    resp = client.get(f"/v1/orgs/{org.id}/accessions", headers=auth_header)
    assert resp.status_code == 200, resp.content
    accessions_json = resp.json()
    assert accessions_json[0]["id"] == accession.id
    assert accessions_json[0]["code"] == accession.code
    assert accessions_json[0]["taxon_id"] == accession.taxon_id


def test_accessions_list_include(client, auth_header, org, accession):
    resp = client.get(
        f"/v1/orgs/{org.id}/accessions?include=taxon", headers=auth_header
    )
    assert resp.status_code == 200, resp.content
    accessions_json = resp.json()
    acc = accessions_json[0]
    assert acc["id"] == accession.id
    assert acc["code"] == accession.code
    assert acc["taxon_id"] == accession.taxon_id
    assert acc["taxon"] is not None, acc["taxon"]
    assert acc["taxon"]["id"] == acc["taxon_id"], acc["taxon"]


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


# def test_accession_items_list(client, auth_header, org, accession, accession_item):
#     resp = client.get(
#         f"/v1/orgs/{org.id}/accessions/{accession.id}/items", headers=auth_header
#     )
#     assert resp.status_code == 200, resp.content
#     items_json = resp.json()
#     assert items_json[0]["id"] == accession_item.id
#     assert items_json[0]["code"] == accession_item.code
#     assert items_json[0]["accession_id"] == accession_item.accession_id
#     assert items_json[0]["location_id"] == accession_item.location_id


def validate_links_header(links, limit):
    for rel, value in links.items():
        url = urlparse(value["url"])
        assert url.scheme == "http"
        qs = parse_qs(url.query)
        assert "cursor" in qs
        cursor = qs["cursor"][0]
        assert isinstance(cursor, str) and len(cursor) > 0
        assert "limit" in qs
        assert qs["limit"][0] == str(limit)


@pytest.mark.parametrize(
    "num_accessions,limit", [(201, 20), (100, 20), (20, 20), (1, 50)]
)
def test_accessions_list_pagination(
    client, auth_header, org, taxon, make_token, num_accessions, limit
):
    accessions = [
        AccessionFactory(org_id=org.id, taxon_id=taxon.id, code=_)
        for _ in range(num_accessions)
    ]
    resp = client.get(
        f"/v1/orgs/{org.id}/accessions?limit={limit}", headers=auth_header
    )
    assert resp.status_code == 200, resp.content
    if num_accessions < limit:
        assert "link" not in resp.headers
        return

    assert "link" in resp.headers, resp.headers
    assert "next" in resp.links
    assert "url" in resp.links["next"]
    validate_links_header(resp.links, limit)

    next_url = resp.links["next"]["url"]
    page_ctr = 1
    while next_url is not None:
        resp = client.get(next_url, headers=auth_header)
        validate_links_header(resp.links, limit)
        next_url = resp.links.get("next", {}).get("url", None)
        page_ctr += 1

    # assert the number of pages times the page length plus the left over is the
    # correct number of items
    assert (page_ctr - 1) * limit + len(accessions) % limit == len(accessions)


# def test_accession_items_create(
#     client, auth_header, make_token, org, accession, location
# ):
#     data = {
#         "code": make_token(),
#         "item_type": "plant",
#         "accession_id": accession.id,
#         "location_id": location.id,
#     }
#     resp = client.post(
#         f"/v1/orgs/{org.id}/accessions/{accession.id}/items",
#         headers=auth_header,
#         json=data,
#     )
#     assert resp.status_code == 201, resp.text
#     item_json = resp.json()
#     print(data)
#     print(item_json)
#     assert isinstance(item_json["id"], int)
#     assert item_json["code"] == data["code"]
#     assert item_json["accession_id"] == data["accession_id"]
#     assert item_json["location_id"] == data["location_id"]
