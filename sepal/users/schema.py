from pydantic import BaseModel


class UserBase(BaseModel):
    username: str
    email: str = None
    full_name: str = None
    disabled: bool = None


class User(UserBase):
    class Config:
        orm_mode = True


class UserInDB(UserBase):
    id: int
    password: str


class UserCreate(UserBase):
    pass
