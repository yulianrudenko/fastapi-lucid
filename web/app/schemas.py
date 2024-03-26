from pydantic import BaseModel, Field, EmailStr
from datetime import datetime


class Token(BaseModel):
    access_token: str


class UserBase(BaseModel):
    first_name: str = Field(
        min_length=2, max_length=110,
        description='First name',
    )


class UserCreate(UserBase):
    email: EmailStr
    password: str = Field(min_length=5, max_length=50)


class UserOut(UserBase):
    id: int
    email: EmailStr
    token: Token

    class Config:
        from_attributes = True


class BasePost(BaseModel):
    pass


class PostCreate(BasePost):
    text: str = Field(
        min_length=2, max_length=50,
        description='Post text'
    )


class PostOut(BasePost):
    id: int | None

    class Config:
        from_attributes = True
