from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Union, List
from datetime import datetime
from uuid import UUID, uuid4


class Token(BaseModel):
    token_uuid: UUID
    issued_at: datetime

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    username: str
    email: Optional[str] = None


class UserCreate(UserBase):
    password: str


class User(UserBase):
    user_uuid: UUID

    hashed_password: str

    level_of_access: int

    tokens: List[Token] = []

    class Config:
        orm_mode = True


class Credentials(BaseModel):
    identifier: Union[str, EmailStr] = Field(
        ..., description="email or username of user"
    )
    password: str

    class Config:
        schema_extra = {
            "example": {
                "identifier": "user_id",
                "password": "password",
            }
        }


# =======
# | old |
# =======

# from __future__ import annotations

import re
import uuid
from datetime import datetime
from enum import Enum
from typing import (
    Any,
    Callable,
    Dict,
    Generic,
    List,
    Optional,
    Protocol,
    TypeVar,
    Union,
)

from pydantic import BaseModel, EmailStr, Field, validator
from pydantic.generics import GenericModel


def custom_charset(cls: Any, value: str) -> str:
    res = re.match(r"^[\w\d_\-]+$", value, re.ASCII | re.MULTILINE)
    if res:
        return value
    else:
        raise ValueError("id must only include ASCII, `-` and `_` symbols ")


class BaseRes(BaseModel):
    response: Any


class SignInRes(BaseRes):
    response: str


class TokenRes(BaseModel):
    token_uuid: uuid.UUID
    issued_by: str = Field(..., description="id of user, who issued a token")
    location: str
    device: str
    issued_at: str = Field(..., description="iso formatted datetime of token creation")


class TokenListRes(BaseModel):
    response: List[TokenRes]


class NewUser(BaseModel):
    user_id: str
    email: EmailStr
    password: str
    user_name: Optional[str] = None

    _validate_user_id_1 = validator("user_id", allow_reuse=True)(custom_charset)


class NewInvitedUser(NewUser):
    invitation_code: str


class UserInfo(BaseModel):
    user_id: str
    email: EmailStr
    user_name: Optional[str] = None
    member_of: Optional[str]
    level_of_access: int = 0

    _validate_user_id_1 = validator("user_id", allow_reuse=True)(custom_charset)


# class FullUserInfo(Credentials, UserInfo):
#     pass


class UserListResponse(BaseModel):
    response: List[UserInfo]


class UserUpdateUserId(BaseModel):
    new_user_id: str

    _validate_new_user_id_1 = validator("new_user_id", allow_reuse=True)(custom_charset)


class UserUpdateName(BaseModel):
    new_user_name: str


class UserUpdatePassword(BaseModel):
    old_password: str
    new_password: str

    @validator("new_password")
    def new_password_cant_be_old_password(cls, new_password, values):
        if "old_password" in values and new_password == values["old_password"]:
            raise ValueError("passwords can't match")
        return new_password


class UserChangePassword(UserUpdatePassword):
    old_password: str


class TokenTester(Protocol):
    def __call__(
        self,
        greater_or_equal: Optional[int] = None,
        one_of: Optional[List[int]] = None,
    ) -> Callable[[str], UserInfo]:
        ...


class MinimalOrganisation(BaseModel):
    organisation_id: str
    organisation_name: Optional[str] = None

    _validate_organisation_id_1 = validator("organisation_id", allow_reuse=True)(
        custom_charset
    )


class OrgListRes(BaseModel):
    response: List[MinimalOrganisation]


class Organisation(MinimalOrganisation):
    users: List[str]


class OrgUpdateOrgId(BaseModel):
    new_organisation_id: str

    _validate_new_organisation_id_1 = validator(
        "new_organisation_id", allow_reuse=True
    )(custom_charset)


class OrgUpdateName(BaseModel):
    new_organisation_name: str


class MinimalInviteCode(BaseModel):
    invitation_code_uuid: uuid.UUID
    code: str = Field(..., min_length=8, max_length=32, regex=r"[\w\d_\-]+")
    add_to: str

    _validate_organisation_id_1 = validator("add_to", allow_reuse=True)(custom_charset)


class InviteCode(MinimalInviteCode):
    issuer_id: str
    num_registered: int


class InviteCodeListRes(BaseModel):
    response: List[InviteCode]
