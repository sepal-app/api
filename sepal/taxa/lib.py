from base64 import b64decode
from contextlib import contextmanager
from enum import Enum
from typing import Literal, List, Optional

from sqlalchemy.orm import joinedload

from sepal.db import Session

from .models import Taxon
from .schema import TaxonCreate, TaxonUpdate


class TaxaPermission(str, Enum):
    Read = "taxa:read"
    Create = "taxa:create"
    Update = "taxa:update"
    Delete = "taxa:delete"


@contextmanager
def taxon_query():
    with Session() as session:
        yield session.query(Taxon)


async def get_taxon_by_id(
    taxon_id: int,
    org_id: Optional[str] = None,
    include: Optional[List[Literal["parent"]]] = None,
) -> Taxon:
    with taxon_query() as q:
        q = q.filter(Taxon.id == taxon_id)
        if org_id:
            q = q.filter(Taxon.org_id == org_id)
        if include is not None:
            for field in include:
                q = q.options(joinedload(getattr(Taxon, field)))

        return q.first()


async def get_taxa(
    org_id: str,
    query: Optional[str] = None,
    limit: int = 50,
    cursor: str = None,
    include: Optional[List[str]] = None,
) -> List[Taxon]:
    with taxon_query() as q:
        # TODO: if name isn't unique then we can't use it as the cursor so
        # ordering by the name also won't work, maybe if have a primary sort by name
        # and a secondary sort by id
        q = q.filter(Taxon.org_id == org_id).order_by(Taxon.name)

        if query is not None:
            q = q.filter(Taxon.name.ilike(f"%{query}%"))

        if cursor is not None:
            decoded_cursor = b64decode(cursor).decode()
            q = q.filter(Taxon.id > decoded_cursor)

        if include is not None:
            for field in include:
                q = q.options(joinedload(getattr(Taxon, field)))

        return q.limit(limit).all()


async def create_taxon(org_id: str, values: TaxonCreate) -> Taxon:
    with Session() as session:
        taxon = Taxon(org_id=org_id, **values.dict())
        session.add(taxon)
        session.commit()
        session.refresh(taxon)
        return taxon


async def update_taxon(taxon_id: int, data: TaxonUpdate) -> Taxon:
    with Session() as session:
        q = session.query(Taxon)
        q.filter(Taxon.id == taxon_id).update(data, synchronize_session=False)
        session.commit()
        taxon = await get_taxon_by_id(taxon_id)
        return taxon
