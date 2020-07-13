from typing import Optional

from passlib.context import CryptContext

from sepal.db import Query, db

# from .models import User as UserModel, user_table
# from .schema import User, UserInDB

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def get_organization_by_id(org_id: str):
    q = organization_table.select().where(organization_table.c.id == org_id)
    data = await db.fetch_one(q)
    return OrganizationInDB(**data) if data else None
