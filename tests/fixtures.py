import asyncio
import secrets

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm.session import object_session
from sqlalchemy.orm import scoped_session, sessionmaker

from sepal.app import app
import sepal.db as _db
from .factories import UserFactory, Session


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
def user(session, password):
    return UserFactory(password=password)
