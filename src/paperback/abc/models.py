from __future__ import annotations

import re
import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Protocol, Union

from pydantic import BaseModel, EmailStr, Field, validator


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
    issued_at: str = Field(
        ..., description="iso formatted datetime of token creation"
    )


class TokenListRes(BaseModel):
    response: List[TokenRes]


class Credentials(BaseModel):
    identifier: Union[str, EmailStr] = Field(...)
    password: str

    class Config:
        schema_extra = {
            "example": {"identifier": "user_id", "password": "password",}
        }


class NewUser(BaseModel):
    user_id: str
    email: EmailStr
    password: str
    user_name: Optional[str] = None

    _validate_user_id_1 = validator("user_id", allow_reuse=True)(
        custom_charset
    )


class NewInvitedUser(NewUser):
    invitation_code: str


class UserInfo(BaseModel):
    user_id: str
    email: EmailStr
    user_name: Optional[str] = None
    member_of: Optional[str]
    level_of_access: int = 0

    _validate_user_id_1 = validator("user_id", allow_reuse=True)(
        custom_charset
    )


# class FullUserInfo(Credentials, UserInfo):
#     pass


class UserListResponse(BaseModel):
    response: List[UserInfo]


class UserUpdateUserId(BaseModel):
    new_user_id: str

    _validate_new_user_id_1 = validator("new_user_id", allow_reuse=True)(
        custom_charset
    )


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

    _validate_organisation_id_1 = validator(
        "organisation_id", allow_reuse=True
    )(custom_charset)


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

    _validate_organisation_id_1 = validator("add_to", allow_reuse=True)(
        custom_charset
    )


class InviteCode(MinimalInviteCode):
    issuer_id: str
    num_registered: int


class InviteCodeListRes(BaseModel):
    response: List[InviteCode]


# +------+
# | Docs |
# +------+


class OwnerType(str, Enum):
    user = "user"
    organisation = "organisation"


class Owner(BaseModel):
    type: OwnerType
    id: str


class CreateDoc(BaseModel):
    doc_id: str
    name: Optional[str] = None
    parent_corp_id: str
    text: str

    private: bool = False
    has_access: Optional[List[str]] = None

    author: Optional[str] = None
    created: Optional[datetime] = None
    tags: Optional[List[str]] = None


class ReadMinimalDoc(BaseModel):
    doc_id: str
    name: Optional[str] = None
    parent_corp_id: str

    private: bool = False


class ReadDoc(ReadMinimalDoc):
    text: str

    owner: OwnerType
    has_access: Optional[List[str]] = None

    author: Optional[str] = None
    created: Optional[datetime] = None
    tags: Optional[List[str]] = None


class ReadDocs(BaseModel):
    response: List[ReadMinimalDoc]


class CreateCorp(BaseModel):
    corp_id: str
    name: Optional[str] = None
    parent_corp_id: Optional[str] = None

    private: bool = False
    has_access: Optional[List[str]] = None
    to_include: List[str] = Field(
        [], description="list of id strings to include into corpus"
    )


class ReadMinimalCorp(BaseModel):
    corp_id: str
    name: Optional[str] = None
    parent_corp_id: Optional[str] = None

    private: bool = False


class ReadCorp(ReadMinimalCorp):
    owner: OwnerType
    has_access: Optional[List[str]] = None
    includes: List[Union[ReadMinimalDoc, ReadMinimalCorp]]


class ReadCorps(BaseModel):
    response: List[ReadMinimalCorp]

    class Config:
        schema_extra = {
            "example": [
                {
                    "corp_id": "corp_1",
                    "corp_name": "Первый корпус",
                },
                {
                    "corp_id": "pushkin_1",
                    "corp_name": "Корпус сочинений Пушкина",
                },
            ]
        }


class CreateDict(BaseModel):
    dict_id: str
    name: Optional[str] = None
    words: List[str] = Field(..., min_length=1)

    private: bool = False
    has_access: Optional[List[str]] = None


class ReadDict(BaseModel):
    dic_id: str
    words: List[str]
    owner: str
    private: bool = False
    name: Optional[str] = None
    has_access: Optional[List[str]] = None
    creator: str


class ReadDicts(BaseModel):
    response: List[ReadDict]


class Entity(BaseModel):
    type: str = Field(..., regex=r"(?:corp(?:us)?)|(?:doc(?:ument)?)")
    id: str


class AnalyzeReq(BaseModel):
    entity_ids: List[Entity] = Field(
        ..., title="list of documents and corpuses to analyze",
    )


class AnalyzeRes(BaseModel):
    entity_id: str
    type: str


class LexicsAnalyzeReq(AnalyzeReq):
    dicts: List[str]


class LexicsAnalyzePreRes(BaseModel):
    source_entity_id: str
    type: str = Field(..., regex=r"(?:corp(?:us)?)|(?:doc(?:ument)?)")
    span: str


class LexicsAnalyzeRes(BaseModel):
    spans: List[LexicsAnalyzePreRes]
    frequencies: Dict[str, Dict[str, float]]


class PredicatesAnalyzeReq(AnalyzeReq):
    argument: Optional[str] = None
    predicate: Optional[str] = None
    role: Optional[str] = None


class PredicatesAnalyzePreRes(AnalyzeRes):
    argument: Optional[str] = None
    predicate: Optional[str] = None
    role: Optional[str] = None
    context: Optional[str] = None


class PredicatesAnalyzeRes(BaseModel):
    response: List[PredicatesAnalyzePreRes]


class AvailableStats(BaseModel):
    response: List[str]


class StatsAnalyzeReq(AnalyzeReq):
    statistics: List[str]


# will be returned as values in a dict
class StatsAnalyzePreRes(AnalyzeRes):
    stat: Dict[str, Union[str, int, float]]


class StatsAnalyzeRes(BaseModel):
    response: List[StatsAnalyzePreRes]


class CompareAnalyzeReq(BaseModel):
    first_set: List[str]
    second_set: List[str]
    statistics: List[str]


class CompareAnalyzeRes(BaseModel):
    first_set: Dict[str, StatsAnalyzePreRes]
    second_set: Dict[str, StatsAnalyzePreRes]
    correlation: Dict[str, Dict[str, Union[int, Dict[str, str]]]]

    # class Config:
    #     schema_extra = {
    #         "example": {
    #             "correlation": {
    #                 "correlation_stat": {
    #                     "value": 3.14,
    #                     "translations": {
    #                         "rus": "",
    #                         "eng": "",
    #                     }
    #                 }
    #             }
    #         }
    #     }
