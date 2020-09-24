from typing import List, Optional

from passlib.context import CryptContext

from sepal.db import db

from .models import location_table
from .schema import LocationCreate, LocationInDB


async def get_location_by_id(
    location_id: int, org_id: Optional[str] = None
) -> LocationInDB:
    q = location_table.select().where(location_table.c.id == location_id)
    if org_id is not None:
        q = q.where(location_table.c.org_id == org_id)

    data = await db.fetch_one(q)
    return LocationInDB(**data) if data else None


async def get_locations(org_id: str, query: Optional[str] = None) -> List[LocationInDB]:
    # TODO: pagination
    q = location_table.select().where(location_table.c.org_id == org_id)
    if query is not None:
        q = q.where(location_table.c.name.ilike(query))
    data = await db.fetch_all(q)
    return [LocationInDB(**d) for d in data]


async def create_location(org_id: str, location: LocationCreate) -> LocationInDB:
    async with db.transaction():
        values = dict(org_id=org_id, **location.dict())
        location_id = await db.execute(location_table.insert(), values=values)
        return await get_location_by_id(location_id)
