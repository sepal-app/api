from typing import List, Optional
from pydantic import BaseModel

from sepal.profile.schema import ProfileSchema
from .models import RoleType


class OrganizationSchemaBase(BaseModel):
    name: str
    short_name: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    postal_code: Optional[str] = None


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


class OrganizationUserSchema(OrganizationUserSchemaBase):
    class Config:
        orm_mode = True


# class OrganizationInDB(OrganizationBase):
#     id: int
class InvitationCreate(BaseModel):
    emails: List[str]
