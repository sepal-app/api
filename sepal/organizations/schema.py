from pydantic import BaseModel


class OrganizationBase(BaseModel):
    name: str
    short_name: str = None
    address: str = None
    city: str = None
    state: str = None
    country: str = None
    postal_code: str = None


class Organization(OrganizationBase):
    class Config:
        orm_mode = True


class OrganizationInDB(OrganizationBase):
    id: int


class OrganizationCreate(OrganizationBase):
    pass
