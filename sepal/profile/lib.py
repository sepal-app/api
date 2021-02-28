from contextlib import contextmanager
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import object_session

import sepal.db as db
from .models import Profile
from .schema import ProfileCreate, ProfileUpdate


async def get_profile(user_id: str) -> Profile:
    with db.Session() as session:
        q = select(Profile).filter_by(user_id=user_id)
        return session.execute(q).scalars().first()


async def create_profile(user_id: str, data: ProfileCreate) -> Profile:
    with db.Session() as session:
        profile = Profile(user_id=user_id, **data.dict())
        session.add(profile)
        session.commit()
        session.refresh(profile)
        return profile


async def update_profile(user_id: str, data: ProfileUpdate) -> Optional[Profile]:
    with db.Session() as session:
        q = select(Profile).filter_by(user_id=user_id)
        profile = session.execute(q).scalars().first()

        if not profile:
            return None

        for key, value in data.dict().items():
            setattr(profile, key, value)

        session.commit()
        session.refresh(profile)
        return profile
