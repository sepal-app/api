from enum import Enum
from itertools import chain
from typing import Union

from fastapi import Depends, HTTPException

from sepal.accessions.lib import AccessionsPermission
from sepal.auth import get_current_user
from sepal.locations.lib import LocationsPermission
from sepal.organizations.lib import (
    OrganizationsPermission,
    get_user_role,
    verify_org_id,
)
from sepal.organizations.models import RoleType
from sepal.taxa.lib import TaxaPermission


class PermissionsPermission(str, Enum):
    Read = "permissions:read"
    Create = "permissions:create"
    Update = "permissions:update"
    Delete = "permissions:delete"


PermissionType = Union[
    AccessionsPermission,
    LocationsPermission,
    OrganizationsPermission,
    PermissionsPermission,
    TaxaPermission,
]

AllPermissions = list(
    chain(
        AccessionsPermission,
        LocationsPermission,
        OrganizationsPermission,
        PermissionsPermission,
        TaxaPermission,
    )
)

RolePermissions = {
    RoleType.Guest: [
        AccessionsPermission.Read,
        LocationsPermission.Read,
        TaxaPermission.Read,
    ],
    RoleType.Member: list(AccessionsPermission)
    + list(LocationsPermission)
    + list(TaxaPermission),
}

RolePermissions[RoleType.Admin] = (
    RolePermissions[RoleType.Member]
    + [
        OrganizationsPermission.Create,
        OrganizationsPermission.Read,
        OrganizationsPermission.Update,
        OrganizationsPermission.UsersList,
        OrganizationsPermission.UsersInvite,
    ]
    + list(PermissionsPermission)
)

RolePermissions[RoleType.Owner] = RolePermissions[RoleType.Admin] + [
    OrganizationsPermission.Delete
]


def check_permission(permission: PermissionType):
    async def _inner(user_id=Depends(get_current_user), org_id=Depends(verify_org_id)):
        if not await has_permission(org_id, user_id, permission):
            raise HTTPException(status_code=403, detail="Insufficient permissions")

    return _inner


async def has_permission(org_id: int, user_id: str, permission: PermissionType):
    """Return True if the user has a permission in an organization."""
    role = await get_user_role(org_id, user_id)
    return permission in RolePermissions.get(role, [])
