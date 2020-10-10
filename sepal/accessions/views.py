from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Response, status, Request

from sepal.auth import get_current_user
from sepal.utils import make_cursor_link

from .lib import create_accession, get_accession_by_id, get_accessions
from .schema import AccessionCreate, AccessionInDB
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
) -> List[AccessionInDB]:
    if org_id is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    accessions = await get_accessions(org_id, q, limit=limit, cursor=cursor)
    if len(accessions) == limit:
        next_url = make_cursor_link(str(request.url), accessions[-1].code, limit)
        response.headers["Link"] = f"<{next_url}>; rel=next"

    return accessions


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
