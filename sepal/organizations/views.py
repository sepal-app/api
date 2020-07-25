from typing import List

from fastapi import APIRouter, Depends, Response, status

from sepal.auth import get_current_user

from .lib import create_organization, get_organization_by_id, get_user_organizations
from .schema import OrganizationCreate, OrganizationInDB

router = APIRouter()


@router.get("")
async def list(current_user_id=Depends(get_current_user)) -> List[OrganizationInDB]:
    return await get_user_organizations(current_user_id)


@router.post("", status_code=status.HTTP_201_CREATED)
async def create(
    org: OrganizationCreate, current_user_id=Depends(get_current_user)
) -> OrganizationInDB:
    return await create_organization(current_user_id, org)


@router.get("/{org_id}")
async def detail(
    org_id: int, response: Response, current_user_id=Depends(get_current_user),
) -> OrganizationInDB:
    org = await get_organization_by_id(org_id, current_user_id)
    if org is None:
        response.status_code = status.HTTP_404_NOT_FOUND
        return None

    return org
