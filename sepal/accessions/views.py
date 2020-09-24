from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status

from sepal.auth import get_current_user

from .lib import create_accession, get_accession_by_id, get_accessions
from .schema import AccessionCreate, AccessionInDB
from sepal.organizations.lib import verify_org_id

router = APIRouter()


@router.get("")
async def list(
    current_user_id=Depends(get_current_user),
    org_id=Depends(verify_org_id),
    q: Optional[str] = None,
) -> List[AccessionInDB]:
    if org_id is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return await get_accessions(org_id, q)


@router.post("", status_code=status.HTTP_201_CREATED)
async def create(
    accession: AccessionCreate,
    current_user_id=Depends(get_current_user),
    org_id=Depends(verify_org_id),
) -> AccessionInDB:
    if org_id is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return await create_accession(org_id, accession)


@router.get("/{accession_id}")
async def detail(
    accession_id: int,
    current_user_id=Depends(get_current_user),
    org_id=Depends(verify_org_id),
) -> AccessionInDB:
    if org_id is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    accession = await get_accession_by_id(accession_id, org_id)
    if accession is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return accession
