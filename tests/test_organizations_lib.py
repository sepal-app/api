from sepal.organizations.lib import create_organization
from sepal.organizations.schema import OrganizationCreate
from sepal.permissions.lib import AllPermissions, has_permission

import pytest

from .factories import OrganizationFactory
from .fixtures import *  # noqa: F401,F403


@pytest.mark.asyncio
async def test_create_organization(db, current_user_id, make_token):
    data = OrganizationCreate(name=make_token())
    org = await create_organization(current_user_id, data)
    assert isinstance(org.id, int)
    assert org.name == data.name

    # check that the user has full permissions on the organization
    for item in AllPermissions:
        assert has_permission(org.id, current_user_id, item)
