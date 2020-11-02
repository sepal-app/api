from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response, status

from sepal.auth import get_current_user
from sepal.utils import create_schema, make_cursor_link

from .lib import create_location, get_location_by_id, get_locations
from .models import Location
from .schema import LocationCreate, LocationInDB, LocationSchema
from sepal.organizations.lib import verify_org_id

router = APIRouter()


@router.get("")
async def list(
    request: Request,
    response: Response,
    current_user_id=Depends(get_current_user),
    org_id=Depends(verify_org_id),
    q: Optional[str] = None,
    cursor: Optional[str] = None,
    limit: int = 50,
    # TODO: what can we include here
    include: Optional[List[str]] = Query(None),
) -> List[LocationSchema]:
    if org_id is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    locations = await get_locations(
        org_id, q, limit=limit, cursor=cursor, include=include
    )
    if len(locations) == limit:
        next_url = make_cursor_link(str(request.url), locations[-1].code, limit)
        response.headers["Link"] = f"<{next_url}>; rel=next"

    # build the schema based on the request parameters
    Schema = create_schema(LocationSchema, Location, include=include)
    return [Schema.from_orm(location) for location in locations]


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
    # TODO: what can we include
    include: Optional[List["str"]] = Query(None),
) -> LocationInDB:
    if org_id is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    location = await get_location_by_id(location_id, org_id, include=include)
    if location is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    Schema = create_schema(LocationSchema, Location, include=include)
    return Schema.from_orm(location)
