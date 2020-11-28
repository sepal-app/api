from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status, Request

from sepal.auth import get_current_user
from sepal.organizations.lib import verify_org_id
from sepal.permissions.lib import check_permission
from sepal.utils import create_schema, make_cursor_link


from .lib import TaxaPermission, create_taxon, get_taxa, get_taxon_by_id, update_taxon
from .models import Taxon
from .schema import TaxonCreate, TaxonSchema, TaxonInDB

router = APIRouter()


@router.get("", dependencies=[Depends(check_permission(TaxaPermission.Read))])
async def list(
    request: Request,
    response: Response,
    current_user_id=Depends(get_current_user),
    org_id=Depends(verify_org_id),
    q: Optional[str] = None,
    cursor: Optional[str] = None,
    limit: int = 50,
    include: Optional[List["parent"]] = Query(None),
) -> List[TaxonSchema]:
    if org_id is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    taxa = await get_taxa(org_id, q, limit=limit, cursor=cursor, include=include)
    if len(taxa) == limit:
        next_url = make_cursor_link(str(request.url), str(taxa[-1].id), limit)
        response.headers["Link"] = f"<{next_url}>; rel=next"

    # build the schema based on the request parameters
    Schema = create_schema(TaxonSchema, Taxon, include=include)
    return [Schema.from_orm(taxon) for taxon in taxa]


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(check_permission(TaxaPermission.Create))],
)
async def create(
    taxon: TaxonCreate,
    current_user_id=Depends(get_current_user),
    org_id=Depends(verify_org_id),
) -> TaxonSchema:
    if org_id is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return await create_taxon(org_id, taxon)


@router.get(
    "/{taxon_id}", dependencies=[Depends(check_permission(TaxaPermission.Read))],
)
async def detail(
    taxon_id: int,
    current_user_id=Depends(get_current_user),
    org_id=Depends(verify_org_id),
    include: Optional[List["parent"]] = Query(None),
) -> TaxonInDB:
    if org_id is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    taxon = await get_taxon_by_id(taxon_id, org_id, include=include)
    if taxon is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    Schema = create_schema(TaxonSchema, Taxon, include=include)
    return Schema.from_orm(taxon)


@router.patch(
    "/{taxon_id}", dependencies=[Depends(check_permission(TaxaPermission.Update))],
)
async def update(
    taxon_id: int,
    taxon: TaxonCreate,
    current_user_id=Depends(get_current_user),
    org_id=Depends(verify_org_id),
) -> TaxonInDB:
    if org_id is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return await update_taxon(taxon_id, taxon)
