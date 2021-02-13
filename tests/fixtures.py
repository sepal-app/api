import secrets
from random import choice

import pytest
from fastapi.testclient import TestClient

import sepal.db as db
from sepal.requestvars import request_global
from sepal.app import app
from sepal.organizations.models import OrganizationUser, RoleType
from sepal.permissions import AllPermissions

from .factories import (
    AccessionFactory,
    AccessionItemFactory,
    LocationFactory,
    OrganizationFactory,
    ProfileFactory,
    Session,
    TaxonFactory,
)


@pytest.fixture
def make_token():
    def _inner(length=6):
        return secrets.token_hex(length)

    return _inner


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def session():
    s = Session()
    yield s
    Session.remove()


@pytest.fixture
def password():
    return secrets.token_hex(32)


@pytest.fixture
def current_user_id(make_token):
    from sepal.auth import get_current_user

    user_id = make_token()

    def _get_current_user():
        request_global().current_user_id = user_id
        return user_id

    app.dependency_overrides[get_current_user] = _get_current_user
    yield user_id
    del app.dependency_overrides[get_current_user]


@pytest.fixture
def profile(session, current_user_id):
    profile = ProfileFactory(user_id=current_user_id)
    yield profile
    session.delete(profile)
    session.commit()


@pytest.fixture
def auth_header(make_token):
    # This token is junk and trying to authorize against it won't work. Instead
    # of override the dependency injector for get_current_user in the
    # current_user_id fixture
    return {"authorization": f"Bearer {make_token()}"}


@pytest.fixture
def org(session, current_user_id):
    org = OrganizationFactory()
    org_user = OrganizationUser(
        organization_id=org.id, user_id=current_user_id, role=RoleType.Owner
    )
    session.add_all([org, org_user])
    session.commit()
    yield org

    session.delete(org)
    session.commit()


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


@pytest.fixture
def random_permission():
    return choice(AllPermissions)
