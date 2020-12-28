import pytest

from sepal.permissions import has_permission
from sepal.organizations.lib import remove_role
from sepal.organizations.models import RoleType

from .fixtures import *  # noqa: F401,F403


@pytest.mark.asyncio
async def test_has_permission(org, current_user_id, random_permission):
    assert await has_permission(org.id, current_user_id, random_permission)


@pytest.mark.asyncio
async def test_has_permission_fails(org, current_user_id, random_permission):
    await remove_role(org.id, current_user_id, RoleType.Owner)
    assert await has_permission(org.id, current_user_id, random_permission) is False
