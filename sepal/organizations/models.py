from typing import Iterator

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    and_,
    cast,
    func,
    text,
    type_coerce,
)
import sqlalchemy.dialects.postgresql as pg
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import backref, object_mapper, relationship

from sepal.db import (
    BaseModel,
    IdMixin,
    Model,
    TimestampMixin,
    db,
    reference_col,
    utcnow,
)

# from sepal.users.models import User


class Organization(Model):
    name = Column(String(128))
    short_name = Column(String(64))
    address = Column(String(1024))
    city = Column(String(64))
    state = Column(String(64))
    country = Column(String(64))
    postal_code = Column(String(32))

    # users = association_proxy(
    #     "organization_users", "user", creator=lambda user: OrganizationUser(user=user)
    # )

    date_approved = Column(DateTime)
    date_created = Column(DateTime, default=utcnow())
    date_suspended = Column(DateTime)


organization_table = Organization.__table__
