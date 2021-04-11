from typing import Literal, Optional

from pydantic import BaseModel


class AccessionSchemaBase(BaseModel):
    code: str
    taxon_id: Optional[str]


class AccessionSchema(AccessionSchemaBase):
    id: str

    class Config:
        orm_mode = True


class AccessionCreate(AccessionSchemaBase):
    pass


class AccessionUpdate(AccessionSchemaBase):
    pass


class AccessionItemSchemaBase(BaseModel):
    code: str
    accession_id: Optional[str]
    location_id: Optional[str]
    item_type: Literal["plant", "seed", "vegetative", "tissue", "other"]


class AccessionItemSchema(AccessionItemSchemaBase):
    id: str

    class Config:
        orm_mode = True


class AccessionItemCreate(AccessionItemSchemaBase):
    pass


class AccessionItemUpdate(AccessionItemSchemaBase):
    pass
