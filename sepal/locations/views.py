from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status

from sepal.auth import get_current_user

from .lib import create_location, get_location_by_id, get_locations
from .schema import LocationCreate, LocationInDB
from sepal.organizations.lib import verify_org_id

router = APIRouter()


@router.get("")
async def list(
    current_user_id=Depends(get_current_user),
    org_id=Depends(verify_org_id),
    q: Optional[str] = None,
) -> List[LocationInDB]:
    if org_id is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return await get_locations(org_id, q)


@router.post("", status_code=status.HTTP_201_CREATED)
async def create(
    location: LocationCreate,
    current_user_id=Depends(get_current_user),
    org_id=Depends(verify_org_id),
) -> LocationInDB:
    if org_id is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return await create_location(org_id, location)


@router.get("/{location_id}")
async def detail(
    location_id: int,
    current_user_id=Depends(get_current_user),
    org_id=Depends(verify_org_id),
) -> LocationInDB:
    if org_id is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    location = await get_location_by_id(location_id, org_id)
    if location is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return location
