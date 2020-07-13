from typing import Optional

from passlib.context import CryptContext

from sepal.db import Query, db

from .models import User as UserModel, user_table
from .schema import User, UserInDB

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def get_user_by_id(user_id: str):
    # table = UserModel.__table__
    q = user_table.select().where(user_table.c.id == user_id)
    data = await db.fetch_one(q)
    return UserInDB(**data) if data else None


async def get_user_by_username(username: str):
    # table = UserModel.__table__
    q = user_table.select().where(user_table.c.username == username)
    data = await db.fetch_one(q)
    return UserInDB(**data) if data else None
    # return session.query(UserModel).filter_by(username=username).first()


def get_user_by_username2(session, username: str):
    return session.query(UserModel).filter_by(username=username).first()
    # q = UserModel.query.filter_by(username=username)
    # data = await db.fetch_one(query=q.statement)
    # re
    # return UserInDB(**data) if data else None


async def authenticate_user(username: str, password: str) -> Optional[User]:
    user = await get_user_by_username(username)
    if not user:
        return None
    if not verify_password(password, user.password):
        return None
    return user
