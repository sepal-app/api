from typing import Optional

from pydantic import BaseModel


class AccessionBase(BaseModel):
    code: str
    taxon_id: Optional[int]


class Accession(AccessionBase):
    class Config:
        orm_mode = True


class AccessionInDB(AccessionBase):
    id: int


class AccessionCreate(AccessionBase):
    pass
