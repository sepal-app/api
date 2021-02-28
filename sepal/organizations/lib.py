import secrets
from contextlib import contextmanager
from enum import Enum
from typing import List, Optional, Tuple

import httpx
from fastapi import Depends, Path
from sqlalchemy import delete, select
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
    with db.Session() as session:
        q = select(OrganizationUser).filter_by(organization_id=org_id, user_id=user_id)
        if role:
            q = q.where(role=role)

        q = select(q.exists())

        return session.execute(q).scalar()


async def get_organization_by_id(
    org_id: int, user_id: Optional[str] = None
) -> Organization:
    """Get the organization.

    If a user_id is provided it will only return the organization if the user
    is a member of the organization.
    """
    with db.Session() as session:
        q = select(Organization).filter_by(id=org_id)
        if user_id is not None:
            q = q.join(OrganizationUser).where(OrganizationUser.user_id == user_id)

        return session.execute(q).scalars().first()


async def get_user_organizations(user_id: str) -> List[Organization]:
    """Get all of the organizations for a user."""
    with db.Session() as session:
        q = (
            select(Organization)
            .join(OrganizationUser)
            .where(OrganizationUser.user_id == user_id)
        )
        return session.execute(q).scalars().all()


async def get_user_role(org_id: int, user_id: str) -> Optional[RoleType]:
    with db.Session() as session:
        q = select(OrganizationUser.role).filter_by(
            organization_id=org_id, user_id=user_id
        )
        role = session.execute(q).scalar()
        return role if role else None


async def assign_role(org_id: int, user_id: str, role: RoleType):
    """Assign a user to a role in an organization."""
    with db.Session() as session:
        q = (
            select(OrganizationUser)
            .filter_by(organization_id=org_id, user_id=user_id, role=role)
            .exists()
        )
        if session.query(q).scalar():
            return

        org_user = OrganizationUser(organization_id=org_id, user_id=user_id, role=role)
        session.add(org_user)
        session.commit()


async def remove_role(org_id: int, user_id: str, role: RoleType):
    """Remove a user from a role in an organization."""
    with db.Session() as session:
        q = delete(OrganizationUser).filter_by(organization_id=org_id, user_id=user_id)
        session.execute(q)
        session.commit()


async def create_organization(user_id: str, data: OrganizationCreate) -> Organization:
    with db.Session() as session:
        org = Organization(**data.dict())
        org_user = OrganizationUser(
            organization=org, user_id=user_id, role=RoleType.Owner
        )
        session.add_all([org, org_user])
        session.commit()
        session.refresh(org)
        return org


async def update_organization(
    org_id: str, data: OrganizationUpdate
) -> Optional[Organization]:
    with db.Session() as session:
        q = select(Organization).filter_by(id=org_id)
        org = session.execute(q).scalar().first()
        if not org:
            return None

        for key, value in data.dict().items():
            setattr(org, key, value)

        session.commit()
        session.refresh(org)
        return org


async def get_users(org_id: int) -> List[Tuple[Profile, RoleType]]:
    with db.Session() as session:
        q = select(Profile, OrganizationUser.role).where(
            OrganizationUser.user_id == Profile.user_id,
            OrganizationUser.organization_id == org_id,
        )
        return session.execute(q).all()


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

    with db.Session() as session:
        session.add(invitation)
        session.commit()

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
