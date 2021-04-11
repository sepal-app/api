import pytest
import sqlalchemy as sa

from sepal.activity.lib import init_session_tracking
from sepal.activity.models import Activity
from sepal.requestvars import request_global

from .fixtures import *  # noqa: F401,F403


@pytest.fixture(autouse=True)
def request_global_user(current_user_id):
    request_global().current_user_id = current_user_id


@pytest.fixture(autouse=True)
def track_session(session):
    unregister = init_session_tracking(session)
    yield
    unregister()


def test_activity_create(session, taxon):
    """Test that an activity isn't created for new objects."""
    activities = (
        session.query(Activity).filter_by(table="taxon", table_id=taxon.id).all()
    )
    assert len(activities) == 1
    assert activities[0].data_before is None
    assert activities[0].data_after["id"] == taxon.id


def test_activity_update(session, taxon, make_token):
    taxon_old_name = taxon.name
    taxon.name = make_token()
    session.commit()
    activities = (
        session.query(Activity)
        .filter(
            Activity.table == "taxon",
            Activity.table_id == taxon.id,
            Activity.data_before["name"].astext == taxon_old_name,
            Activity.data_after["name"].astext == taxon.name,
        )
        .all()
    )

    # session.delete(activities[0])
    # session.commit()
    assert len(activities) == 1


def test_activity_delete(session, taxon):
    session.delete(taxon)
    session.commit()
    activities = (
        session.query(Activity)
        .filter(
            Activity.table == "taxon",
            Activity.table_id == taxon.id,
            Activity.data_before["name"].astext == taxon.name,
            Activity.data_after == sa.JSON.NULL,
        )
        .all()
    )
    assert len(activities) == 1, activities
