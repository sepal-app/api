from typing import List, Optional

from passlib.context import CryptContext

from sepal.db import db

from .models import taxon_table
from .schema import TaxonCreate, TaxonInDB


async def get_taxon_by_id(taxon_id: int, org_id: Optional[str] = None) -> TaxonInDB:
    q = taxon_table.select().where(taxon_table.c.id == taxon_id)
    if org_id is not None:
        q = q.where(taxon_table.c.org_id == org_id)

    data = await db.fetch_one(q)
    return TaxonInDB(**data) if data else None


async def get_taxa(org_id: str, query: Optional[str] = None) -> List[TaxonInDB]:
    # TODO: pagination
    q = taxon_table.select().where(taxon_table.c.org_id == org_id)
    if query is not None:
        q = q.where(taxon_table.c.name.ilike(query))
    data = await db.fetch_all(q)
    return [TaxonInDB(**d) for d in data]


async def create_taxon(org_id: str, taxon: TaxonCreate) -> TaxonInDB:
    async with db.transaction():
        values = dict(org_id=org_id, **taxon.dict())
        taxon_id = await db.execute(taxon_table.insert(), values=values)
        return await get_taxon_by_id(taxon_id)
