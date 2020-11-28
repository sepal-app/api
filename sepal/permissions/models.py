import enum

from sqlalchemy import Column, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import backref, relationship
from sqlalchemy.schema import UniqueConstraint

from sepal.db import Model


class RoleType(str, enum.Enum):
    Admin = "admin"
    Guest = "guest"
    Member = "member"
    Owner = "owner"


class Role(Model):
    __table_args__ = (
        UniqueConstraint("organization_id", "name"),
        {"extend_existing": True},
    )
    organization_id = Column(Integer, ForeignKey("organization.id"), nullable=False)
    organization = relationship(
        "Organization", backref=backref("roles", cascade="all, delete-orphan")
    )
    # TODO: use an enum for
    name = Column(String, nullable=False)


class RoleMember(Model):
    __table_args__ = (
        UniqueConstraint("role_id", "user_id"),
        {"extend_existing": True},
    )
    # TODO: setup an association proxy so we can get all the users for a role
    # and all the roles for a user
    role_id = Column(Integer, ForeignKey("role.id"), nullable=False)
    role = relationship(
        "Role", backref=backref("_members", cascade="all, delete-orphan")
    )
    user_id = Column(String, nullable=False)


class RolePermission(Model):
    __table_args__ = (
        UniqueConstraint("role_id", "name"),
        {"extend_existing": True},
    )
    role_id = Column(Integer, ForeignKey("role.id"), nullable=False)
    role = relationship(
        "Role", backref=backref("permissions", cascade="all, delete-orphan")
    )
    name = Column(String, nullable=False)


class UserPermission(Model):
    __table_args__ = (
        UniqueConstraint("user_id", "organization_id", "name"),
        {"extend_existing": True},
    )
    user_id = Column(String, nullable=False)
    organization_id = Column(Integer, ForeignKey("organization.id"), nullable=False)
    organization = relationship(
        "Organization",
        backref=backref("_user_permissions", cascade="all, delete-orphan"),
    )

    # TODO: should the name be an enum of all the possible permissions or
    # should we maybe have a join table of the permissions list so we can add
    # permissions to the database without a schema change
    name = Column(String, nullable=False)
