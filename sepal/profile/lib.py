from contextlib import contextmanager
from typing import Optional

from sqlalchemy.orm import object_session

from sepal.db import Session
from .models import Profile
from .schema import ProfileCreate, ProfileSchema, ProfileUpdate


@contextmanager
def profile_query():
    with Session() as session:
        yield session.query(Profile)


async def get_profile(user_id: str) -> Profile:
    with profile_query() as q:
        return q.filter_by(user_id=user_id).first()


async def create_profile(user_id: str, data: ProfileCreate) -> Profile:
    with Session() as session:
        profile = Profile(user_id=user_id, **data.dict())
        session.add(profile)
        session.commit()
        session.refresh(profile)
        return profile


async def update_profile(user_id: str, data: ProfileUpdate) -> Optional[Profile]:
    with profile_query() as q:
        profile = q.filter_by(user_id=user_id).first()
        if not profile:
            return None

        for key, value in data.dict().items():
            setattr(profile, key, value)

        session = object_session(profile)
        session.commit()
        session.refresh(profile)
        return profile
