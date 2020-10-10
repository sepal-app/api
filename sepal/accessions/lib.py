from typing import List, Optional
from base64 import b64decode

from sepal.db import db

from .models import accession_table, accession_item_table
from .schema import (
    AccessionCreate,
    AccessionInDB,
    AccessionItemCreate,
    AccessionItemInDB,
)


async def get_accession_by_id(
    accession_id: int, org_id: Optional[str] = None
) -> AccessionInDB:
    q = accession_table.select().where(accession_table.c.id == accession_id)
    if org_id is not None:
        q = q.where(accession_table.c.org_id == org_id)

    data = await db.fetch_one(q)
    return AccessionInDB(**data) if data else None


async def get_accessions(
    org_id: str, query: Optional[str] = None, limit: int = 50, cursor: str = None
) -> List[AccessionInDB]:
    q = (
        accession_table.select()
        .where(accession_table.c.org_id == org_id)
        .limit(limit)
        .order_by(accession_table.c.code)
    )
    if query is not None:
        q = q.where(accession_table.c.code.ilike(query))

    if cursor is not None:
        decoded_cursor = b64decode(cursor).decode()
        q = q.where(accession_table.c.code > decoded_cursor)

    data = await db.fetch_all(q.limit(limit))
    return [AccessionInDB(**d) for d in data]


async def create_accession(org_id: str, accession: AccessionCreate) -> AccessionInDB:
    async with db.transaction():
        values = dict(org_id=org_id, **accession.dict())
        accession_id = await db.execute(accession_table.insert(), values=values)
        return await get_accession_by_id(accession_id)


async def get_accession_item_by_id(
    accession_item_id: int, org_id: Optional[str] = None
) -> AccessionItemInDB:
    q = accession_item_table.select().where(
        accession_item_table.c.id == accession_item_id
    )
    if org_id is not None:
        q = q.where(accession_item_table.c.org_id == org_id)

    data = await db.fetch_one(q)
    return AccessionItemInDB(**data) if data else None


async def get_accession_items(
    org_id: str, accession_id, int, query: Optional[str] = None
) -> List[AccessionItemInDB]:
    # TODO: pagination
    q = (
        accession_item_table.select()
        .where(accession_item_table.c.org_id == org_id)
        .where(accession_item_table.c.accession_id == accession_id,)
    )
    if query is not None:
        q = q.where(accession_item_table.c.code.ilike(query))
    data = await db.fetch_all(q)
    return [AccessionItemInDB(**d) for d in data]


async def create_accession_item(
    org_id: str, accession_item: AccessionItemCreate
) -> AccessionItemInDB:
    async with db.transaction():
        values = dict(org_id=org_id, **accession_item.dict())
        print("values: ")
        print(values)
        accession_item_id = await db.execute(
            accession_item_table.insert(), values=values
        )
        return await get_accession_item_by_id(accession_item_id)
