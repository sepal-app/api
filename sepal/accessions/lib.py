from base64 import b64decode
from contextlib import contextmanager
from enum import Enum
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import joinedload

import sepal.db as db

from .models import Accession, AccessionItem
from .schema import (
    AccessionCreate,
    AccessionItemCreate,
    AccessionItemUpdate,
    AccessionUpdate,
)


class AccessionsPermission(str, Enum):
    Read = "accessions:read"
    Create = "accessions:create"
    Update = "accessions:update"
    Delete = "accessions:delete"


async def get_accession_by_id(
    accession_id: int,
    org_id: Optional[str] = None,
    include: Optional[List[str]] = None,
) -> Accession:
    with db.Session() as session:
        q = select(Accession).where(Accession.id == accession_id)
        if org_id:
            q = q.where(Accession.org_id == org_id)
        if include is not None:
            for field in include:
                q = q.options(joinedload(getattr(Accession, field)))

        return session.execute(q).scalars().first()


async def get_accessions(
    org_id: str,
    query: Optional[str] = None,
    limit: int = 50,
    cursor: Optional[str] = None,
    include: Optional[List[str]] = None,
) -> List[Accession]:
    with db.Session() as session:
        q = select(Accession).where(Accession.org_id == org_id).order_by(Accession.code)

        if query is not None:
            q = q.where(Accession.code.ilike(f"%{query}%"))

        if cursor is not None:
            decoded_cursor = b64decode(cursor).decode()
            q = q.where(Accession.code > decoded_cursor)

        if include is not None:
            for field in include:
                q = q.options(joinedload(getattr(Accession, field)))

        q = q.limit(limit)

        return session.execute(q).scalars().all()


async def create_accession(org_id: str, values: AccessionCreate) -> Accession:
    with db.Session() as session:
        accession = Accession(org_id=org_id, **values.dict())
        session.add(accession)
        session.commit()
        session.refresh(accession)
        return accession


async def update_accession(accession_id: int, values: AccessionUpdate) -> Accession:
    with db.Session() as session:
        accession = session.get(Accession, accession_id)

        # use setattr on the instance instead of using the faster query.update()
        # so that the before_flush event gets fired
        for key, value in values.dict().items():
            setattr(accession, key, value)

        session.commit()
        session.refresh(accession)
        return accession


# async def get_accession_item_by_id(
#     accession_item_id: int, org_id: Optional[str] = None
# ) -> AccessionItem:
#     with Session() as session:
#         q = session.query(AccessionItem).filter_by(id=accession_item_id)
#         if org_id is not None:
#             q = q.filter_by(org_id=org_id)

#         return q.first()


async def get_accession_items(
    org_id: str,
    accession_id: str,
    query: Optional[str] = None,
    # limit: int = 50,
    # cursor: Optional[str] = None,
    include: Optional[List[str]] = None,
) -> List[Accession]:
    with db.Session() as session:
        q = (
            select(AccessionItem)
            .where(AccessionItem.org_id == org_id)
            .where(AccessionItem.accession_id == accession_id)
            .order_by(AccessionItem.code)
        )

        if query is not None:
            q = q.where(AccessionItem.code.ilike(f"%{query}%"))

        # if cursor is not None:
        #     decoded_cursor = b64decode(cursor).decode()
        #     q = q.where(AccessionItem.code > decoded_cursor)

        if include is not None:
            for field in include:
                q = q.options(joinedload(getattr(AccessionItem, field)))

        # q = q.limit(limit)

        return session.execute(q).scalars().all()


async def create_accession_item(
    org_id: str, values: AccessionItemCreate
) -> AccessionItem:
    with db.Session() as session:
        item = AccessionItem(org_id=org_id, **values.dict())
        session.add(item)
        session.commit()
        session.refresh(item)
        return item


async def update_accession_item(
    accession_item_id: int, values: AccessionItemUpdate
) -> AccessionItem:
    with db.Session() as session:
        item = session.get(AccessionItem, accession_item_id)

        # use setattr on the instance instead of using the faster query.update()
        # so that the before_flush event gets fired
        for key, value in values.dict().items():
            setattr(item, key, value)

        session.commit()
        session.refresh(item)
        return item
