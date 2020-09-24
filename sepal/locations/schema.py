from typing import Optional

from pydantic import BaseModel


class LocationBase(BaseModel):
    name: str
    code: str
    description: Optional[str]


class Location(LocationBase):
    class Config:
        orm_mode = True


class LocationInDB(LocationBase):
    id: int


class LocationCreate(LocationBase):
    pass
