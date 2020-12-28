from typing import Literal, Optional

from pydantic import BaseModel


class AccessionSchemaBase(BaseModel):
    code: str
    taxon_id: Optional[int]


class AccessionSchema(AccessionSchemaBase):
    id: int

    class Config:
        orm_mode = True


class AccessionInDB(AccessionSchema):
    pass
    # id: int


class AccessionCreate(AccessionSchemaBase):
    pass


class AccessionUpdate(AccessionSchemaBase):
    pass


class AccessionItemSchemaBase(BaseModel):
    code: str
    accession_id: Optional[int]
    location_id: Optional[int]
    item_type: Literal["plant", "seed", "vegetative", "tissue", "other"]


class AccessionItemSchema(AccessionItemSchemaBase):
    class Config:
        orm_mode = True


class AccessionItemInDB(AccessionItemSchema):
    id: int


class AccessionItemCreate(AccessionItemSchemaBase):
    pass


class AccessionItemUpdate(AccessionItemSchemaBase):
    pass
