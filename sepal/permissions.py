from enum import Enum
from itertools import chain
from typing import Dict, List, Union

from fastapi import Depends, HTTPException

from sepal.accessions.lib import AccessionsPermission
from sepal.activity.lib import ActivityPermission
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
    ActivityPermission,
    LocationsPermission,
    OrganizationsPermission,
    PermissionsPermission,
    TaxaPermission,
]

AllPermissions: List[PermissionType] = list(
    chain(
        AccessionsPermission,
        ActivityPermission,
        LocationsPermission,
        OrganizationsPermission,
        PermissionsPermission,
        TaxaPermission,
    )
)

# Define the permissions allowed by each role type
RolePermissions: Dict[RoleType, List[PermissionType]] = {}

# Guests
RolePermissions[RoleType.Guest] = [
    AccessionsPermission.Read,
    LocationsPermission.Read,
    TaxaPermission.Read,
]

# Organization Members
RolePermissions[RoleType.Member] = list(
    chain(AccessionsPermission, ActivityPermission, LocationsPermission, TaxaPermission)
)

# Organization Admins
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

# Organization Owners
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
    if role is None:
        return False
    return permission in RolePermissions.get(role, [])
