from typing import Optional

from pydantic import BaseModel


class TaxonBase(BaseModel):
    name: str
    rank: str
    parent_id: Optional[int]


class Taxon(TaxonBase):
    class Config:
        orm_mode = True


class TaxonInDB(TaxonBase):
    id: int


class TaxonCreate(TaxonBase):
    pass
