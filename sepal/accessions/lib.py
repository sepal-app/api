from typing import List, Optional

from sepal.db import db

from .models import accession_table
from .schema import AccessionCreate, AccessionInDB


async def get_accession_by_id(
    accession_id: int, org_id: Optional[str] = None
) -> AccessionInDB:
    q = accession_table.select().where(accession_table.c.id == accession_id)
    if org_id is not None:
        q = q.where(accession_table.c.org_id == org_id)

    data = await db.fetch_one(q)
    return AccessionInDB(**data) if data else None


async def get_accessions(
    org_id: str, query: Optional[str] = None
) -> List[AccessionInDB]:
    # TODO: pagination
    q = accession_table.select().where(accession_table.c.org_id == org_id)
    if query is not None:
        q = q.where(accession_table.c.code.ilike(query))
    data = await db.fetch_all(q)
    return [AccessionInDB(**d) for d in data]


async def create_accession(org_id: str, accession: AccessionCreate) -> AccessionInDB:
    async with db.transaction():
        values = dict(org_id=org_id, **accession.dict())
        accession_id = await db.execute(accession_table.insert(), values=values)
        return await get_accession_by_id(accession_id)
