from typing import List

from fastapi import APIRouter, Depends, HTTPException, Path, Response, status

from sepal.auth import get_current_user

from .lib import create_taxon, get_taxon_by_id, get_taxa
from .schema import TaxonCreate, TaxonInDB
from sepal.organizations.lib import is_organization_member

router = APIRouter()


async def verify_org_id(
    current_user_id=Depends(get_current_user), org_id: int = Path(...),
):
    is_member = await is_organization_member(org_id, current_user_id)
    return org_id if is_member else None


@router.get("")
async def list(
    current_user_id=Depends(get_current_user), org_id=Depends(verify_org_id),
) -> List[TaxonInDB]:
    if org_id is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return await get_taxa(org_id)


@router.post("", status_code=status.HTTP_201_CREATED)
async def create(
    taxon: TaxonCreate,
    current_user_id=Depends(get_current_user),
    org_id=Depends(verify_org_id),
    response=Response,
) -> TaxonInDB:
    if org_id is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return await create_taxon(org_id, taxon)


@router.get("/{taxon_id}")
async def detail(
    taxon_id: int,
    current_user_id=Depends(get_current_user),
    org_id=Depends(verify_org_id),
) -> TaxonInDB:
    if org_id is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    taxon = await get_taxon_by_id(taxon_id, org_id)
    if taxon is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return taxon
