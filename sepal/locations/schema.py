from typing import Optional

from pydantic import BaseModel


class LocationBase(BaseModel):
    name: str
    code: str
    description: Optional[str]


class LocationSchema(LocationBase):
    id: str

    class Config:
        orm_mode = True


class LocationCreate(LocationBase):
    pass


class LocationUpdate(LocationBase):
    pass
