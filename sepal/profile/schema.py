from typing import Optional

from pydantic import BaseModel


class ProfileSchemaBase(BaseModel):
    family_name: Optional[str] = ""
    given_name: Optional[str] = ""
    name: Optional[str] = ""
    phone_number: Optional[str] = ""
    picture: Optional[str] = ""


class ProfileSchema(ProfileSchemaBase):
    email: str
    user_id: str

    class Config:
        orm_mode = True


class ProfileCreate(ProfileSchemaBase):
    email: str


class ProfileUpdate(ProfileSchemaBase):
    pass
