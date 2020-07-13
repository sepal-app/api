import datetime as dt

import sqlalchemy.dialects.postgresql as pg
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy import (
    Binary,
    Boolean,
    Column,
    ForeignKey,
    Integer,
    String,
    Table,
)
from sqlalchemy.orm import relationship

import sepal.db as db
from sepal.log import log

client_id_length = 32


class User(db.Model):
    """A user of the app."""

    username = Column(String(64), unique=True, nullable=False)
    email = Column(String(64), unique=True, nullable=False)
    password = Column(String(128), nullable=False)
    family_name = Column(String(64), nullable=True)
    given_name = Column(String(64), nullable=True)
    # active = Column(Boolean(), default=False)

    scopes = Column(pg.ARRAY(String), nullable=False, default=[])

    organization_id = Column(
        Integer, ForeignKey("organizations.id", ondelete="CASCADE")
    )

    organization = relationship("Organization", back_populates="users")

    def __init__(self, username, email, password=None, **kwargs):
        """Create instance."""
        db.Model.__init__(self, username=username, email=email, **kwargs)
        if password:
            self.set_password(password)
        else:
            self.password = None

    def set_password(self, password):
        """Set password."""
        from .lib import get_password_hash

        self.password = get_password_hash(password)

    @property
    def full_name(self):
        """Full user name."""
        return "{0} {1}".format(self.first_name, self.last_name)

    def __repr__(self):
        """Represent instance as a unique string."""
        return "<User({username!r})>".format(username=self.username)


user_table = User.__table__
