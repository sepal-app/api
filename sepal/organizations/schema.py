from typing import List
from pydantic import BaseModel

from sepal.profile.schema import ProfileSchema
from .models import RoleType


class OrganizationSchemaBase(BaseModel):
    name: str
    short_name: str = None
    address: str = None
    city: str = None
    state: str = None
    country: str = None
    postal_code: str = None


class OrganizationSchema(OrganizationSchemaBase):
    id: int

    class Config:
        orm_mode = True


# class OrganizationInDB(OrganizationBase):
#     id: int


class OrganizationCreate(OrganizationSchemaBase):
    pass


class OrganizationUpdate(OrganizationSchemaBase):
    pass


class OrganizationUserSchemaBase(BaseModel):
    profile: ProfileSchema
    role: RoleType


class OrganizationUserSchema(OrganizationSchemaBase):
    class Config:
        orm_mode = True


# class OrganizationInDB(OrganizationBase):
#     id: int
class InvitationCreate(BaseModel):
    emails: List[str]
