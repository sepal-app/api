import enum

from sqlalchemy import Column, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import backref, relationship

from sepal.db import Model
from sepal.organizations.models import Organization


class Rank(enum.Enum):
    Kingdom = "kingdom"
    Phylum = "phylum"
    Class = "class"
    Order = "order"
    Family = "family"
    Tribe = "tribe"
    Genus = "genus"
    Section = "section"
    Series = "series"
    Species = "species"
    Variety = "variety"
    Form = "form"


class Taxon(Model):
    __track_activity__ = True

    name = Column(String(128), nullable=False)
    rank = Column(
        Enum(
            Rank,
            name="taxon_rank_enum",
            values_callable=lambda _: [rank.value for rank in Rank],
        ),
        nullable=False,
    )

    parent_id = Column(Integer, ForeignKey("taxon.id"), nullable=True)
    org_id = Column(Integer, ForeignKey("organization.id"), nullable=False)

    organization: Organization = relationship(
        Organization, backref=backref("taxa", cascade="all, delete-orphan")
    )


# declare outside the class definition since we need to reference Taxon.id
Taxon.parent = relationship(Taxon, uselist=False, remote_side=Taxon.id)
