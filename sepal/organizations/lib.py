from enum import Enum
from contextlib import contextmanager
from itertools import chain
from typing import List, Optional, Tuple

from fastapi import Depends, Path
from sqlalchemy import exists, select

from sepal.accessions.lib import AccessionsPermission
from sepal.auth import get_current_user
from sepal.db import Session
from sepal.locations.lib import LocationsPermission
from sepal.profile.models import Profile
from sepal.taxa.lib import TaxaPermission

from .models import Organization, OrganizationUser, RoleType
from .schema import OrganizationCreate


class OrganizationsPermission(str, Enum):
    Create = "organizations:create"
    Delete = "organizations:delete"
    Read = "organizations:read"
    UsersInvite = "organizations:users_invite"
    UsersList = "organizations:users_list"
    Update = "organizations:update"


@contextmanager
def organization_query():
    with Session() as session:
        yield session.query(Organization)


@contextmanager
def organization_user_query():
    with Session() as session:
        yield session.query(OrganizationUser)


async def verify_org_id(
    current_user_id=Depends(get_current_user), org_id: int = Path(...),
) -> Optional[int]:
    """Return True/False if the current user is a member of an organization"""
    return org_id if await is_member(org_id, current_user_id) else None


async def is_member(org_id: int, user_id: str, role: Optional[RoleType] = None) -> bool:
    with Session() as session:
        q = session.query(OrganizationUser).filter_by(
            organization_id=org_id, user_id=user_id
        )
        if role:
            q = q.filter_by(role=role)

        return session.query(q.exists()).scalar()


async def get_organization_by_id(
    org_id: int, user_id: Optional[str] = None
) -> Organization:
    with organization_query() as q:
        q = q.filter_by(id=org_id)
        if user_id is not None:
            q = q.join(OrganizationUser).filter(OrganizationUser.user_id == user_id)

        return q.first()


async def get_user_organizations(user_id: str) -> List[Organization]:
    with organization_query() as q:
        return (
            q.join(OrganizationUser).filter(OrganizationUser.user_id == user_id).all()
        )


async def get_user_role(org_id: int, user_id: str) -> Optional[RoleType]:
    with organization_user_query() as q:
        org_user = q.filter_by(organization_id=org_id, user_id=user_id).first()
        return org_user.role if org_user else None


async def assign_role(org_id: int, user_id: str, role: RoleType):
    """Assign a user to a role in an organization."""
    with Session() as session:
        org_user_exists = (
            session.query(OrganizationUser)
            .filter_by(organization_id=org_id, user_id=user_id, role=role)
            .exists()
        )
        if session.query(org_user_exists).scalar():
            return

        org_user = OrganizationUser(organization_id=org_id, user_id=user_id, role=role)
        session.add(org_user)
        session.commit()


async def remove_role(org_id: int, user_id: str, role: RoleType):
    """Remove a user from a role in an organization."""
    with Session() as session:
        session.query(OrganizationUser).filter_by(
            organization_id=org_id, user_id=user_id
        ).delete()
        session.commit()


async def create_organization(user_id: str, data: OrganizationCreate) -> Organization:
    with Session() as session:
        org = Organization(**data.dict())
        org_user = OrganizationUser(
            organization=org, user_id=user_id, role=RoleType.Owner
        )
        session.add_all([org, org_user])
        session.commit()
        session.refresh(org)
        return org


async def get_users(org_id: int) -> Tuple[Profile, RoleType]:
    with Session() as session:
        return (
            session.query(Profile, OrganizationUser.role)
            .filter(
                OrganizationUser.user_id == Profile.user_id,
                OrganizationUser.organization_id == org_id,
            )
            .all()
        )
