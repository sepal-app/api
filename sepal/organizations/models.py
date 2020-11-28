from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import backref, relationship

from sepal.db import BaseModel, Model, utcnow


class Organization(Model):
    name = Column(String(128))
    short_name = Column(String(64))
    address = Column(String(1024))
    city = Column(String(64))
    state = Column(String(64))
    country = Column(String(64))
    postal_code = Column(String(32))
    date_approved = Column(DateTime)
    date_created = Column(DateTime, server_default=utcnow())
    date_suspended = Column(DateTime)


organization_table = Organization.__table__


class OrganizationUser(BaseModel):
    user_id = Column(String, nullable=False, primary_key=True)
    organization_id = Column(
        Integer, ForeignKey("organization.id"), nullable=False, primary_key=True
    )

    organization = relationship(
        "Organization",
        backref=backref("organization_users", cascade="all, delete-orphan"),
    )


organization_user_table = OrganizationUser.__table__
