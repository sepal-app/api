from enum import Enum
from functools import partial
from itertools import chain
from typing import Literal, Union

from fastapi import Depends, HTTPException
from sqlalchemy import or_, text, literal

from sepal.db import Session
from sepal.accessions.lib import AccessionsPermission
from sepal.auth import get_current_user
from sepal.locations.lib import LocationsPermission
from sepal.organizations.lib import OrganizationsPermission, verify_org_id
from sepal.organizations.models import (
    Organization,
    OrganizationUser,
    organization_table,
)
from sepal.taxa.lib import TaxaPermission

from .models import Role, RoleMember, RolePermission, RoleType, UserPermission


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
    ]
    + list(PermissionsPermission)
)

RolePermissions[RoleType.Owner] = RolePermissions[RoleType.Admin] + [
    OrganizationsPermission.Delete
]


def check_permission(permission: PermissionType):
    def _inner(user_id=Depends(get_current_user), org_id=Depends(verify_org_id)):
        if not has_permission(org_id, user_id, permission):
            raise HTTPException(status_code=403, detail="Insufficient permissions")

    return _inner


def has_permission(org_id: int, user_id: str, permission: PermissionType):
    """Return True if the user or one of the user's role's has permission"""
    with Session() as session:
        user_permission_exists_query = session.query(UserPermission).filter_by(
            organization_id=org_id, user_id=user_id, name=permission.value
        )

        users_role_permission_exists_query = (
            session.query(Role)
            .join(RoleMember)
            .join(RolePermission)
            .filter(
                Role.organization_id == org_id,
                RoleMember.user_id == user_id,
                RolePermission.name == permission.value,
            )
        )

        q = session.query(literal(1)).filter(
            or_(
                user_permission_exists_query.exists(),
                users_role_permission_exists_query.exists(),
            )
        )
        return session.query(q.exists()).scalar()


def grant_user_permission(org_id: str, user_id: str, permission: PermissionType):
    """Grant a named permission to a user in an organization"""
    with Session() as session:
        permission = UserPermission(
            organization_id=org_id, user_id=user_id, name=permission.value
        )
        session.add(permission)
        session.commit()


def revoke_user_permission(org_id: int, user_id: str, permission: PermissionType):
    """Revoke a named permission from a user in an organization"""
    with Session() as session:
        session.query(UserPermission).filter_by(
            organization_id=org_id, user_id=user_id, name=permission.value
        ).delete()
        session.commit()


def grant_role_permission(role_id: int, permission: PermissionType):
    """Grant a named permission to a role in an organization"""
    with Session() as session:
        perm = RolePermission(role_id=role_id, name=permission.value)
        session.add(perm)
        session.commit()


def revoke_role_permission(role_id: int, permission: PermissionType):
    """Revoke a named permission to a role in an organization."""
    with Session() as session:
        p = session.query(RolePermission).filter_by(
            role_id=role_id, name=permission.value
        )
        print(list(p.all()))
        session.query(RolePermission).filter_by(
            role_id=role_id, name=permission.value
        ).delete()
        session.commit()


def assign_user_role(user_id: str, role_id: int):
    """Assign a user to a role."""
    with Session() as session:
        member = RoleMember(user_id=user_id, role_id=role_id)
        session.add(member)
        session.commit()


def remove_user_role(user_id: str, role_id: int):
    """Remove a user from a role."""
    with Session() as session:
        session.query(RoleMember).filter_by(user_id=user_id, role_id=role_id).delete()
        session.commit()


def is_role_member(user_id: str, role_id: int):
    """Return True/False if a user is a member of the role."""
    with Session() as session:
        q = session.query(RoleMember).filter_by(user_id=user_id, role_id=role_id)
        return session.query(q.exists()).scalar()
