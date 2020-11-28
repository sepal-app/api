from typing import List

from fastapi import APIRouter, Depends, HTTPException, Response, status

from sepal.auth import get_current_user
from sepal.permissions import check_permission

from .lib import (
    OrganizationsPermission,
    create_organization,
    get_organization_by_id,
    get_users,
    get_user_organizations,
)
from .models import Organization
from .schema import OrganizationCreate, OrganizationSchema, OrganizationUserSchema

router = APIRouter()


@router.get(
    "", response_model=List[OrganizationSchema],
)
async def list(current_user_id=Depends(get_current_user)) -> List[Organization]:
    """Return the list of the user's organizations.

    There's no permission check b/c a user can always return a list of the
    organizations they belong to.

    """
    return await get_user_organizations(current_user_id)


@router.post(
    "", status_code=status.HTTP_201_CREATED,
)
async def create(
    org: OrganizationCreate, current_user_id=Depends(get_current_user)
) -> Organization:
    """Create a new organization.

    There's no permission check b/c a user can always create a new organization.
    """
    return await create_organization(current_user_id, org)


@router.get("/{org_id}", response_model=OrganizationSchema)
async def detail(
    org_id: int, response: Response, current_user_id=Depends(get_current_user),
) -> Organization:
    """Get the organization details."""
    org = await get_organization_by_id(org_id, current_user_id)
    if org is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return org


@router.get(
    "/{org_id}/invite",
    dependencies=[Depends(check_permission(OrganizationsPermission.UsersInvite))],
)
async def invite(
    org_id: int, response: Response, current_user_id=Depends(get_current_user),
):
    org = await get_organization_by_id(org_id, current_user_id)
    if org is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return org


@router.get(
    "/{org_id}/users",
    dependencies=[Depends(check_permission(OrganizationsPermission.UsersList))],
    # response_model=OrganizationUserSchema,
)
async def users(
    org_id: int,
    response: Response,
    current_user_id=Depends(get_current_user),
    response_model=OrganizationUserSchema,
):
    org = await get_organization_by_id(org_id, current_user_id)
    if org is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    result = await get_users(org_id)
    return [{"profile": profile, "role": role} for profile, role in result]
