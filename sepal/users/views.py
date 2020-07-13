from fastapi import APIRouter

from .lib import get_user_by_id
from .schema import User

router = APIRouter()


@router.get("/{user_id}")
async def detail(user_id: int):
    user = await get_user_by_id(user_id)
    return user
