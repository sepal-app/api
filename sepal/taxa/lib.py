from base64 import b64decode
from enum import Enum
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import joinedload

import sepal.db as db

from .models import Taxon
from .schema import TaxonCreate, TaxonUpdate


class TaxaPermission(str, Enum):
    Read = "taxa:read"
    Create = "taxa:create"
    Update = "taxa:update"
    Delete = "taxa:delete"


async def get_taxon_by_id(
    taxon_id: int,
    org_id: Optional[str] = None,
    include: Optional[List[str]] = None,
) -> Taxon:
    with db.Session() as session:
        q = select(Taxon).where(Taxon.id == taxon_id)
        if org_id:
            q = q.where(Taxon.org_id == org_id)
        if include is not None:
            for field in include:
                q = q.options(joinedload(getattr(Taxon, field)))

        return session.execute(q).scalars().first()


async def get_taxa(
    org_id: str,
    query: Optional[str] = None,
    limit: int = 50,
    cursor: Optional[str] = None,
    include: Optional[List[str]] = None,
) -> List[Taxon]:

    with db.Session() as session:
        # TODO: if name isn't unique then we can't use it as the cursor so
        # ordering by the name also won't work, maybe if have a primary sort by name
        # and a secondary sort by id
        q = select(Taxon).where(Taxon.org_id == org_id).order_by(Taxon.name)

        if query is not None:
            q = q.where(Taxon.name.ilike(f"%{query}%"))

        if cursor is not None:
            decoded_cursor = b64decode(cursor).decode()
            q = q.where(Taxon.id > decoded_cursor)

        if include is not None:
            for field in include:
                q = q.options(joinedload(getattr(Taxon, field)))

        q = q.limit(limit)

        return session.execute(q).scalars().all()


async def create_taxon(org_id: str, values: TaxonCreate) -> Taxon:
    with db.Session() as session:
        taxon = Taxon(org_id=org_id, **values.dict())
        session.add(taxon)
        session.commit()
        session.refresh(taxon)
        return taxon


async def update_taxon(taxon_id: int, values: TaxonUpdate) -> Taxon:
    with db.Session() as session:
        taxon = session.get(Taxon, taxon_id)

        # use setattr on the instance instead of using the faster query.update()
        # so that the before_flush event gets fired
        for key, value in values.dict().items():
            setattr(taxon, key, value)

        session.commit()
        session.refresh()
        return taxon
