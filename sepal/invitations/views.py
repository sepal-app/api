from typing import List

from fastapi import APIRouter, Depends, HTTPException, Response, status

from sepal.auth import get_current_user
from sepal.permissions import check_permission

from .lib import accept_invitation

router = APIRouter()


@router.post(
    "/{token}/accept",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,  # required for 204 response
)
async def accept(
    token: str, current_user_id=Depends(get_current_user),
):
    if not await accept_invitation(token, current_user_id):
        # The token was invalid
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
