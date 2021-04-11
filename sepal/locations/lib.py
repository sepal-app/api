from base64 import b64decode
from contextlib import contextmanager
from enum import Enum
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import joinedload

import sepal.db as db
from .models import Location
from .schema import LocationCreate, LocationSchema, LocationUpdate


class LocationsPermission(str, Enum):
    Read = "locations:read"
    Create = "locations:create"
    Update = "locations:update"
    Delete = "locations:delete"


async def get_location_by_id(
    location_id: int,
    org_id: Optional[str] = None,
    include: Optional[List[str]] = None,
) -> Location:
    with db.Session() as session:
        q = select(Location).where(
            Location.org_id == org_id, Location.id == location_id
        )
        if include is not None:
            for field in include:
                q = q.options(joinedload(getattr(Location, field)))

        return session.execute(q).scalars().first()


async def get_locations(
    org_id: str,
    query: Optional[str] = None,
    limit: int = 50,
    cursor: str = None,
    include: Optional[List[str]] = None,
) -> List[Location]:
    with db.Session() as session:
        q = select(Location).where(Location.org_id == org_id).order_by(Location.code)

        if query is not None:
            q = q.where(Location.code.ilike(f"%{query}%"))

        if cursor is not None:
            decoded_cursor = b64decode(cursor).decode()
            q = q.where(Location.code > decoded_cursor)

        if include is not None:
            for field in include:
                q = q.options(joinedload(getattr(Location, field)))

        q = q.limit(limit)

        return session.execute(q).scalars().all()


async def create_location(org_id: str, values: LocationCreate) -> LocationSchema:
    with db.Session() as session:
        location = Location(org_id=org_id, **values.dict())
        session.add(location)
        session.commit()
        session.refresh(location)
        return location
