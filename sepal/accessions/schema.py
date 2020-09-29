from typing import Literal, Optional

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


class AccessionItemBase(BaseModel):
    code: str
    accession_id: Optional[int]
    location_id: Optional[int]
    item_type: Literal["plant", "seed", "vegetative", "tissue", "other"]


class AccessionItem(AccessionItemBase):
    class Config:
        orm_mode = True


class AccessionItemInDB(AccessionItemBase):
    id: int


class AccessionItemCreate(AccessionItemBase):
    pass
