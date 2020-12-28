import enum

from sqlalchemy import Column, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import backref, relationship

from sepal.db import Model

ranks = [
    "kingdom",
    "phylum",
    "class",
    "order",
    "family",
    "tribe",
    "genus",
    "section",
    "series",
    "species",
    "variety",
    "form",
]

Rank = enum.Enum("Rank", [(r.capitalize(), r) for r in ranks])


class Taxon(Model):
    name = Column(String(128), nullable=False)
    rank = Column(
        Enum(Rank, name="taxon_rank_enum", values_callable=lambda _: ranks,),
        nullable=False,
    )

    parent_id = Column(Integer, ForeignKey("taxon.id"), nullable=True)
    org_id = Column(Integer, ForeignKey("organization.id"), nullable=False)

    organization = relationship(
        "Organization", backref=backref("taxa", cascade="all, delete-orphan")
    )


# declare outside the class definition since we need to reference Taxon.id
Taxon.parent = relationship(Taxon, uselist=False, remote_side=Taxon.id)

taxon_table = Taxon.__table__
