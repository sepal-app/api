from fastapi import APIRouter, Depends, HTTPException, status

from sepal.auth import get_current_user

from .lib import create_profile, get_profile, update_profile
from .models import Profile
from .schema import ProfileCreate, ProfileSchema, ProfileUpdate

router = APIRouter()


@router.get("", response_model=ProfileSchema)
async def detail(current_user_id=Depends(get_current_user)) -> Profile:
    profile = await get_profile(current_user_id)
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return profile


@router.post("", status_code=status.HTTP_201_CREATED, response_model=ProfileSchema)
async def create(
    profile: ProfileCreate, current_user_id=Depends(get_current_user)
) -> Profile:
    existing_profile = await get_profile(current_user_id)
    if existing_profile:
        # can only create a profile if one doesn't already exist for this user
        raise HTTPException(status_code=status.HTTP_409_CONFLICT)

    return await create_profile(current_user_id, profile)


@router.patch("", response_model=ProfileSchema)
async def update(
    profile: ProfileUpdate, current_user_id=Depends(get_current_user)
) -> Profile:
    updated_profile = await update_profile(current_user_id, profile)
    if not updated_profile:
        # can't update a profile if one hasn't been created for the user
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return updated_profile
