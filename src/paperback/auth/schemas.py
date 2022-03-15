from __future__ import annotations

from pydantic import BaseModel, EmailStr, Field, UUID4
from datetime import datetime


# tokens


class TokenBase(BaseModel):
    issued_at: datetime
    user_uuid: UUID4


class CreateToken(TokenBase):
    pass


class TokenOut(TokenBase):
    token_uuid: UUID4

    class Config:
        orm_mode = True


class Token(TokenOut):
    user: User

    class Config:
        orm_mode = True


# user


class UserBase(BaseModel):
    username: str
    email: str | None = None


class UserCreate(UserBase):
    password: str


class UserOut(UserBase):
    level_of_access: int

    class Config:
        orm_mode = True


class User(UserOut):
    user_uuid: UUID4
    hashed_password: str

    tokens: list[Token] = []


# makes Token.user work
Token.update_forward_refs()


class Credentials(BaseModel):
    identifier: str | EmailStr = Field(..., description="email or username of user")
    password: str

    class Config:
        schema_extra = {
            "example": {
                "identifier": "user_id",
                "password": "password",
            }
        }
