import enum

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import backref, relationship

from sepal.db import BaseModel, Model


class Accession(Model):
    code = Column(String(64), nullable=False)

    taxon_id = Column(Integer, ForeignKey("taxon.id"), nullable=False)
    org_id = Column(Integer, ForeignKey("organization.id"), nullable=False)

    organization = relationship(
        "Organization", backref=backref("accessions", cascade="all, delete-orphan")
    )


accession_table = Accession.__table__


AccessionItemType = enum.Enum(
    "AccessionItemType", ["plant", "seed", "vegetative", "tissue", "other"]
)


class AccessionItem(Model):
    code = Column(String(12), nullable=False)
    item_type = Column(String, Enum(AccessionItemType), nullable=False)

    accession_id = Column(Integer, ForeignKey("accession.id"), nullable=False)
    location_id = Column(Integer, ForeignKey("location.id"), nullable=False)
    org_id = Column(Integer, ForeignKey("organization.id"), nullable=False)

    organization = relationship(
        "Organization", backref=backref("accession_items", cascade="all, delete-orphan")
    )


accession_item_table = AccessionItem.__table__
