from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import backref, relationship

from sepal.db import Model


class Taxon(Model):
    name = Column(String(128), nullable=False)
    rank = Column(String(128), nullable=False)

    parent_id = Column(Integer, ForeignKey("taxon.id"), nullable=True)
    org_id = Column(Integer, ForeignKey("organization.id"), nullable=False)

    organization = relationship(
        "Organization", backref=backref("taxa", cascade="all, delete-orphan")
    )


taxon_table = Taxon.__table__
