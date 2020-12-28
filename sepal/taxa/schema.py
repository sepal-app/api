from enum import Enum
from typing import Optional

from pydantic import BaseModel, validator
from .models import Rank


class TaxonSchemaBase(BaseModel):
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


class TaxonSchema(TaxonSchemaBase):
    id: int

    class Config:
        orm_mode = True


class TaxonInDB(TaxonSchema):
    id: int


class TaxonCreate(TaxonSchemaBase):
    pass


class TaxonUpdate(TaxonSchemaBase):
    pass
