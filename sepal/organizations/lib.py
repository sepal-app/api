from typing import List, Optional

from passlib.context import CryptContext
from sqlalchemy import exists, select

from sepal.db import db

from .models import organization_table, organization_user_table
from .schema import OrganizationCreate, OrganizationInDB

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def user_organizations_query(user_id: str):
    return (
        organization_table.join(
            organization_user_table,
            organization_table.c.id == organization_user_table.c.organization_id,
        )
        .select()
        .where(organization_user_table.c.user_id == user_id)
    )


async def is_organization_member(org_id: int, user_id: str):
    q = select([exists(user_organizations_query(user_id))])
    return (await db.fetch_one(q))[0]


async def get_organization_by_id(
    org_id: int, user_id: Optional[str] = None
) -> OrganizationInDB:
    q = (
        user_organizations_query(user_id).where(organization_table.c.id == org_id)
        if user_id is not None
        else organization_table.select().where(organization_table.c.id == org_id)
    )
    data = await db.fetch_one(q)
    return OrganizationInDB(**data) if data else None


async def get_user_organizations(user_id: str) -> List[OrganizationInDB]:
    q = user_organizations_query(user_id)
    data = await db.fetch_all(q)
    return [OrganizationInDB(**d) for d in data]


async def create_organization(
    user_id: str, org: OrganizationCreate
) -> OrganizationInDB:
    async with db.transaction():
        org_id = await db.execute(organization_table.insert(), values=org.dict())
        await db.execute(
            organization_user_table.insert(),
            values={"organization_id": org_id, "user_id": user_id},
        )
        return await get_organization_by_id(org_id)
