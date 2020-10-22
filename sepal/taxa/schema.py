from enum import Enum
from typing import Literal, Optional

from pydantic import BaseModel, validator
from .models import Rank


class TaxonBase(BaseModel):
    name: str
    rank: Rank
    parent_id: Optional[int]

    @validator("rank", pre=True)
    def rank_name(cls, v):
        if isinstance(v, Rank):
            return v

        if not hasattr(Rank, v.capitalize()):
            raise ValueError("invalid rank value")
        return Rank[v.capitalize()]

    class Config:
        json_encoders = {
            Enum: lambda v: v.name.lower(),
        }


class Taxon(TaxonBase):
    class Config:
        orm_mode = True


class TaxonInDB(TaxonBase):
    id: int


class TaxonCreate(TaxonBase):
    pass
