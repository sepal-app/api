from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Response, Request, status

from sepal.auth import get_current_user
from sepal.utils import create_schema, make_cursor_link

from .lib import (
    create_accession,
    # create_accession_item,
    get_accession_by_id,
    get_accessions,
    # get_accession_items,
    update_accession,
)
from .models import Accession
from .schema import (
    AccessionCreate,
    AccessionInDB,
    AccessionItemCreate,
    AccessionItemInDB,
    AccessionSchema,
    AccessionUpdate,
)
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
    include: Optional[List["taxon"]] = Query(None),
) -> List[AccessionSchema]:
    if org_id is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    accessions = await get_accessions(
        org_id, q, limit=limit, cursor=cursor, include=include
    )
    if len(accessions) == limit:
        next_url = make_cursor_link(str(request.url), accessions[-1].code, limit)
        response.headers["Link"] = f"<{next_url}>; rel=next"

    # build the schema based on the request parameters
    Schema = create_schema(AccessionSchema, Accession, include=include)
    return [Schema.from_orm(accession) for accession in accessions]


@router.post("", status_code=status.HTTP_201_CREATED)
async def create(
    accession: AccessionCreate,
    current_user_id=Depends(get_current_user),
    org_id=Depends(verify_org_id),
) -> AccessionSchema:
    if org_id is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return await create_accession(org_id, accession)


@router.get("/{accession_id}")
async def detail(
    accession_id: int,
    current_user_id=Depends(get_current_user),
    org_id=Depends(verify_org_id),
    include: Optional[List["taxon"]] = Query(None),
) -> AccessionSchema:
    if org_id is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    accession = await get_accession_by_id(accession_id, org_id, include=include)
    if accession is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    Schema = create_schema(AccessionSchema, Accession, include=include)
    return Schema.from_orm(accession)


@router.patch("/{accession_id}")
async def update(
    accession_id: int,
    accession: AccessionCreate,
    current_user_id=Depends(get_current_user),
    org_id=Depends(verify_org_id),
) -> AccessionInDB:
    if org_id is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return await update_accession(accession_id, accession)


# @router.get("/{accession_id}/items")
# async def list_items(
#     accession_id: int,
#     org_id=Depends(verify_org_id),
#     current_user_id=Depends(get_current_user),
#     q: Optional[str] = None,
# ) -> List[AccessionInDB]:
#     if org_id is None:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

#     return await get_accession_items(org_id, accession_id, q)


# @router.post("/{accession_id}/items", status_code=status.HTTP_201_CREATED)
# async def create_item(
#     accession_item: AccessionItemCreate,
#     accession_id: int,
#     current_user_id=Depends(get_current_user),
#     org_id=Depends(verify_org_id),
# ) -> AccessionInDB:
#     if org_id is None:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
#     return await create_accession_item(org_id, accession_item)
