import sepal.users.lib as lib

# from sepal.db import Session

import pytest
from .fixtures import *


@pytest.mark.asyncio
async def test_get_by_username2(db, user):
    user2 = await lib.get_by_username2(session, user.username)
    assert user2.id == user.id


@pytest.mark.asyncio
async def test_get_by_username_none(db, user, make_token):
    user2 = await lib.get_by_username2(session, make_token())
    assert user2 is None


def test_get_by_username(session, user):
    user2 = lib.get_by_username(session, user.username)
    assert user2.id == user.id


def test_get_by_username_none(session, user, make_token):
    user2 = lib.get_by_username(session, make_token())
    assert user2 is None
