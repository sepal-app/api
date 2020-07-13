from typing import Any, Dict, List

from fastapi import APIRouter, Depends, Header

from .lib import get_organization_by_id
from sepal.settings import settings
from sepal.auth import decode_token, require_scopes

# from .schema import User

router = APIRouter()


@router.get("")
# async def list(authorization: str = Header(None)):
# async def list(scopes: List[str] = Depends(require_scopes(["test"])),):
async def list(scopes: List[str] = Depends(require_scopes(["openid"])),):
    return []


@router.get("/{org_id}")
async def detail(org_id: int):
    org = await get_organization_by_id(org_id)
    return org
