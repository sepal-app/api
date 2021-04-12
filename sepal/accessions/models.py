import enum
from typing import Literal

from sqlalchemy import Column, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import backref, declared_attr, relationship
from sqlalchemy.schema import UniqueConstraint

from sepal.db import Model

AccessionPermission = Literal[
    "accessions:read",
    "accessions:create",
    "accessions.update",
    "accessions.delete",
]


class Accession(Model):
    __track_activity__ = True

    @declared_attr
    def __table_args__(cls):
        """Return the arguments for Table()."""
        return (UniqueConstraint("org_id", "code"), Model.__table_args__)

    code = Column(String(64), nullable=False)
    taxon_id = Column(Integer, ForeignKey("taxon.id"), nullable=False)
    org_id = Column(Integer, ForeignKey("organization.id"), nullable=False)

    organization = relationship(
        "Organization", backref=backref("accessions", cascade="all, delete-orphan")
    )

    taxon = relationship(
        "Taxon", backref=backref("accessions", cascade="all, delete-orphan")
    )


# The SQLAlchemy enum type will persist the names rather than the values
AccessionItemType = enum.Enum(
    "AccessionItemType", ["plant", "seed", "vegetative", "tissue", "other"]
)


class AccessionItem(Model):
    __track_activity__ = True

    @declared_attr
    def __table_args__(cls):
        """Return the arguments for Table()."""
        return (UniqueConstraint("org_id", "code"), Model.__table_args__)

    code = Column(String(12), nullable=False)
    item_type = Column(String, Enum(AccessionItemType), nullable=False)

    accession_id = Column(Integer, ForeignKey("accession.id"), nullable=False)
    accession = relationship(
        "Accession", backref=backref("items", cascade="all, delete-orphan")
    )
    location_id = Column(Integer, ForeignKey("location.id"), nullable=False)
    location = relationship(
        "Location", backref=backref("accession_items", cascade="all, delete-orphan")
    )
    org_id = Column(Integer, ForeignKey("organization.id"), nullable=False)
    organization = relationship(
        "Organization", backref=backref("accession_items", cascade="all, delete-orphan")
    )
