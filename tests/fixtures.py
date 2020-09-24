import secrets

import pytest
from fastapi.testclient import TestClient

import sepal.db as _db
from sepal.app import app
from sepal.organizations.models import OrganizationUser

from .factories import (
    AccessionFactory,
    AccessionItemFactory,
    LocationFactory,
    OrganizationFactory,
    Session,
    TaxonFactory,
)


@pytest.fixture
def make_token():
    def _inner(length=6):
        return secrets.token_hex(length)

    return _inner


@pytest.fixture
def client(db):
    return TestClient(app)


@pytest.fixture
def session():
    s = Session()
    yield s
    Session.remove()


@pytest.fixture
async def db():
    if not _db.db.is_connected:
        await _db.db.connect()

    yield _db.db

    await _db.db.disconnect()


@pytest.fixture
def password():
    return secrets.token_hex(32)


@pytest.fixture
def current_user_id(make_token):
    from sepal.auth import get_current_user

    user_id = make_token()
    app.dependency_overrides[get_current_user] = lambda: user_id
    yield user_id
    del app.dependency_overrides[get_current_user]


@pytest.fixture
def auth_header(make_token):
    return {"authorization": f"Bearer {make_token()}"}


@pytest.fixture
def org(session, current_user_id):
    org = OrganizationFactory()
    org_user = OrganizationUser(organization_id=org.id, user_id=current_user_id)
    session.add(org_user)
    session.commit()
    return org


@pytest.fixture
def taxon(org):
    return TaxonFactory(org_id=org.id)


@pytest.fixture
def location(org):
    return LocationFactory(org_id=org.id)


@pytest.fixture
def accession(org, taxon):
    return AccessionFactory(org_id=org.id, taxon_id=taxon.id)


@pytest.fixture
def accession_item(org, accession, location):
    return AccessionItemFactory(
        org_id=org.id, accession_id=accession.id, location_id=location.id
    )
