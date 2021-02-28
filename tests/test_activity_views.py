import pytest

from sqlalchemy import event

from sepal.activity.lib import init_session_tracking

from .fixtures import *  # noqa: F401,F403


@pytest.fixture(autouse=True)
def request_global_user(current_user_id):
    request_global().current_user_id = current_user_id


@pytest.fixture(autouse=True)
def track_session(session):
    unregister = init_session_tracking(session)
    yield
    unregister()


# def make_activity(org, taxon, accession, location):
#     pass


@pytest.mark.asyncio
async def test_activity_dummy(
    client,
    auth_header,
    org,
    current_user_id,
    taxon,
    accession,
    location,
    session,
    make_token,
    profile,
):

    # taxon_old_name = taxon.name
    taxon.name = make_token()
    session.commit()

    from sepal.activity.lib import get_activity
    from sepal.activity.schema import ActivitySchema

    activity = await get_activity(org.id)
    d = ActivitySchema.from_orm(activity[0])


def test_activity_list(
    client,
    auth_header,
    org,
    current_user_id,
    taxon,
    accession,
    location,
    session,
    make_token,
):

    # taxon_old_name = taxon.name
    taxon.name = make_token()
    session.commit()

    resp = client.get(f"/v1/orgs/{org.id}/activity", headers=auth_header)
    assert resp.status_code == 200, resp.content
    activity_json = resp.json()
    assert len(activity_json) > 0
    # assert activity_json[0]["id"] == location.id
    # assert activity_json[0]["name"] == location.name
