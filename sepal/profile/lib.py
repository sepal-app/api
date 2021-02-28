from contextlib import contextmanager
from typing import Optional

from sqlalchemy.orm import object_session

import sepal.db as db
from .models import Profile
from .schema import ProfileCreate, ProfileUpdate


@contextmanager
def profile_query():
    yield db.Session().query(Profile)


async def get_profile(user_id: str) -> Profile:
    with profile_query() as q:
        return q.filter_by(user_id=user_id).first()


async def create_profile(user_id: str, data: ProfileCreate) -> Profile:
    session = db.Session()
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

        session = db.Session()
        session.commit()
        session.refresh(profile)
        return profile
