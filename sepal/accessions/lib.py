from base64 import b64decode
from contextlib import contextmanager
from enum import Enum
from typing import List, Literal, Optional

from sqlalchemy.orm import joinedload

from sepal.db import Session, db
from sepal.taxa.models import Taxon

from .models import Accession, accession_table, accession_item_table
from .schema import (
    AccessionCreate,
    AccessionInDB,
    AccessionItemCreate,
    AccessionItemInDB,
    AccessionUpdate,
    AccessionSchema,
    TaxonSchema,
)


class AccessionsPermission(str, Enum):
    Read = "accessions:read"
    Create = "accessions:create"
    Update = "accessions:update"
    Delete = "accessions:delete"


@contextmanager
def accession_query():
    with Session() as session:
        yield session.query(Accession)


async def get_accession_by_id(
    accession_id: int,
    org_id: Optional[str] = None,
    include: Optional[List[str]] = None,
) -> Accession:
    with accession_query() as q:
        q = q.filter(Accession.org_id == org_id, Accession.id == accession_id)
        if include is not None:
            for field in include:
                q = q.options(joinedload(getattr(Accession, field)))

        return q.first()


async def get_accessions(
    org_id: str,
    query: Optional[str] = None,
    limit: int = 50,
    cursor: str = None,
    include: Optional[List[str]] = None,
) -> List[Accession]:
    with accession_query() as q:
        q = q.filter(Accession.org_id == org_id).order_by(Accession.code)

        if query is not None:
            q = q.filter(Accession.code.ilike(f"%{query}%"))

        if cursor is not None:
            decoded_cursor = b64decode(cursor).decode()
            q = q.filter(Accession.code > decoded_cursor)

        if include is not None:
            for field in include:
                q = q.options(joinedload(getattr(Accession, field)))

        return q.limit(limit).all()


async def create_accession(org_id: str, values: AccessionCreate) -> AccessionInDB:
    with Session() as session:
        accession = Accession(org_id=org_id, **values.dict())
        session.add(accession)
        session.commit()
        session.refresh(accession)
        return accession


async def update_accession(accession_id: int, data: AccessionUpdate) -> AccessionInDB:
    # TODO: use the orm
    async with db.transaction():
        await db.execute(
            accession_table.update().where(accession_table.c.id == accession_id),
            values=data.dict(),
        )
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
