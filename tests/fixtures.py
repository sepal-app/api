import secrets
import time
from datetime import datetime, timedelta

import pytest
from fastapi.testclient import TestClient
from jose import jwt as _jwt

import sepal.db as _db
from sepal.app import app
from sepal.organizations.models import OrganizationUser
from sepal.settings import settings

from .factories import OrganizationFactory, Session


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


# @pytest.fixture
# def jwt(current_user_id):
#     now = int(time.time())
#     jwt_payload = _jwt.encode(
#         {"exp": datetime.utcnow() + timedelta(seconds=30)},
#         "secret",
#         "HS256"
#         # settings.token_algorithm,
#     )
#     return jwt_payload
#     return _jwt.encode(
#         {
#             "iss": settings.token_issuer,
#             "sub": current_user_id,
#             "aud": [settings.token_audience],
#             # "iat": now,
#             "exp": datetime.utcnow() + timedelta(seconds=30),
#             # "azp": "",
#             # "scope": "",
#             # "permissions": [],
#         },
#         settings.token_secret,
#         # issuer=settings.token_issuer,
#         # audience=settings.token_audience,
#         # algorithm=os.environ["TOKEN_ALGORITHM"],
#         algorithm=settings.token_algorithm,
#     )
#     # return {
#     #     "iss": "https://sepal-app-local.us.auth0.com/",
#     #     "sub": "auth0|5f091753652e5a0019ce67e8",
#     #     "aud": ["sepal-api-local", "https://sepal-app-local.us.auth0.com/userinfo"],
#     #     "iat": 1595295365,
#     #     "exp": 1595381765,
#     #     "azp": "V087P5U1v7QgKHNoIXgLUw6X7hgoErJN",
#     #     "scope": "openid profile email",
#     #     "permissions": [],
#     # }


@pytest.fixture
def org(session, current_user_id):
    org = OrganizationFactory()
    org_user = OrganizationUser(organization_id=org.id, user_id=current_user_id)
    session.add(org_user)
    session.commit()
    print(org_user.organization_id)
    print(org_user.user_id)
    return org


# @pytest.fixture
# def user(session, password):
#     return UserFactory(password=password)
