from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import backref, relationship

from sepal.db import Model


class Invitation(Model):
    organization_id = Column(Integer, ForeignKey("organization.id"), nullable=False,)
    organization = relationship(
        "Organization", backref=backref("invitations", cascade="all, delete-orphan"),
    )

    token = Column(String, nullable=False, unique=True)
    # The user_id of the user who sent the invite
    invited_by = Column(String, nullable=False)
    email = Column(String, nullable=False)
    acknowledged = Column(DateTime)
