import secrets
from contextlib import contextmanager
from enum import Enum
from typing import List, Optional, Tuple

import httpx
from fastapi import Depends, Path
from sqlalchemy.orm import object_session

import sepal.db as db
from sepal.auth import get_current_user
from sepal.profile.lib import get_profile
from sepal.profile.models import Profile
from sepal.invitations.models import Invitation
from sepal.requestvars import request_global
from sepal.settings import settings
from sepal.templates import get_template

from .models import Organization, OrganizationUser, RoleType
from .schema import OrganizationCreate, OrganizationUpdate


class OrganizationsPermission(str, Enum):
    Create = "organizations:create"
    Delete = "organizations:delete"
    Read = "organizations:read"
    UsersInvite = "organizations:users_invite"
    UsersList = "organizations:users_list"
    Update = "organizations:update"


@contextmanager
def organization_query():
    yield db.Session().query(Organization)


@contextmanager
def organization_user_query():
    yield db.Session().query(OrganizationUser)


async def verify_org_id(
    current_user_id=Depends(get_current_user),
    org_id: int = Path(...),
) -> Optional[int]:
    """Return True/False if the current user is a member of an organization."""
    if await is_member(org_id, current_user_id):
        if current_user_id == request_global().current_user_id:
            request_global().current_org_id = org_id
        return org_id
    return None


async def is_member(org_id: int, user_id: str, role: Optional[RoleType] = None) -> bool:
    with organization_user_query() as q:
        q = q.filter_by(organization_id=org_id, user_id=user_id)
        if role:
            q = q.filter_by(role=role)

        return db.Session().query(q.exists()).scalar()


async def get_organization_by_id(
    org_id: int, user_id: Optional[str] = None
) -> Organization:
    """Get the organization.

    If a user_id is provided it will only return the organization if the user
    is a member of the organization.
    """
    with organization_query() as q:
        q = q.filter_by(id=org_id)
        if user_id is not None:
            q = q.join(OrganizationUser).filter(OrganizationUser.user_id == user_id)

        return q.first()


async def get_user_organizations(user_id: str) -> List[Organization]:
    """Get all of the organizations for a user."""
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
    with organization_user_query() as q:
        org_user_exists = q.filter_by(
            organization_id=org_id, user_id=user_id, role=role
        ).exists()
        session = db.Session()
        if session.query(org_user_exists).scalar():
            return

        org_user = OrganizationUser(organization_id=org_id, user_id=user_id, role=role)
        session.add(org_user)
        session.flush()


async def remove_role(org_id: int, user_id: str, role: RoleType):
    """Remove a user from a role in an organization."""
    with organization_user_query() as q:
        q.filter_by(organization_id=org_id, user_id=user_id).delete()
        db.Session().flush()


async def create_organization(user_id: str, data: OrganizationCreate) -> Organization:
    org = Organization(**data.dict())
    org_user = OrganizationUser(organization=org, user_id=user_id, role=RoleType.Owner)
    session = db.Session()
    session.add_all([org, org_user])
    session.flush()
    session.refresh(org)
    return org


async def update_organization(
    org_id: str, data: OrganizationUpdate
) -> Optional[Organization]:
    with organization_query() as q:
        org = q.filter_by(id=org_id).first()
        if not org:
            return None

        for key, value in data.dict().items():
            setattr(org, key, value)

        session = db.Session()
        session.flush()
        session.refresh(org)
        return org


async def get_users(org_id: int) -> List[Tuple[Profile, RoleType]]:
    return (
        db.Session()
        .query(Profile, OrganizationUser.role)
        .filter(
            OrganizationUser.user_id == Profile.user_id,
            OrganizationUser.organization_id == org_id,
        )
        .all()
    )


async def invite_user(org_id: int, invited_by_user_id: str, email: str):
    # TODO: if the user already has a user account/profile maybe we just add
    # them directly to the organization and send them an email telling
    # them
    token = secrets.token_urlsafe(16)
    invitation = Invitation(
        organization_id=org_id,
        invited_by=invited_by_user_id,
        email=email,
        token=token,
    )

    session = db.Session()
    session.add(invitation)
    session.flush()

    profile = await get_profile(invited_by_user_id)
    org = await get_organization_by_id(org_id)

    template = get_template("invitation.jinja2.html")
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            settings.mailgun_api_url,
            auth=("api", settings.mailgun_api_key),
            data={
                "from": "Sepal Support <noreply@sepal.app>",
                "subject": "You have been invited to join Sepal",
                "html": template.render(
                    url=f"{settings.app_base_url}/register?invitation={token}",
                    invited_by=profile.email,
                    organization_name=org.name,
                ),
                "to": email,
            },
        )

        resp.raise_for_status()
