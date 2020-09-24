from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import backref, relationship

from sepal.db import BaseModel, Model


class Location(Model):
    name = Column(String(64), nullable=False)
    code = Column(String(64), nullable=False)
    description = Column(String(512))

    org_id = Column(Integer, ForeignKey("organization.id"), nullable=False)

    organization = relationship(
        "Organization", backref=backref("locations", cascade="all, delete-orphan")
    )


location_table = Location.__table__
