from typing import Optional

from pydantic import BaseModel, PrivateAttr


class ProfileSchemaBase(BaseModel):
    family_name: str
    given_name: str
    name: str
    phone_number: str
    picture: str


class ProfileSchema(ProfileSchemaBase):
    email: str
    user_id: str

    class Config:
        orm_mode = True


class ProfileCreate(ProfileSchemaBase):
    email: str
    family_name: str = ""
    given_name: str = ""
    name: str = ""
    phone_number: str = ""
    picture: str = ""


class ProfileUpdate(ProfileSchemaBase):
    family_name: Optional[str] = ""
    given_name: Optional[str] = ""
    name: Optional[str] = ""
    phone_number: Optional[str] = ""
    picture: Optional[str] = ""
