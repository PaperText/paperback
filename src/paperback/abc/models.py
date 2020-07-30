from __future__ import annotations

import re
from typing import Any, Dict, List, Union, Callable, Optional, Protocol
from datetime import datetime

from pydantic import Field, BaseModel, validator


def custom_charset(cls: Any, value: str) -> str:
    res = re.match(r"^[\w\d:_\-]+$", value, re.ASCII | re.MULTILINE)
    if res:
        return value
    else:
        raise ValueError(
            "id must only include ASCII, `-` and `_` symbols "
            "and only include one `:`."
        )


def starts_with(sw: str) -> Callable[[Any, str], str]:
    def func(cls: Any, value: str) -> str:
        if value.startswith(sw):
            return value
        else:
            if ":" in value:
                raise ValueError(
                    f"id must start with {sw} and not include other :"
                )
            else:
                return sw + value

    return func


class BaseRes(BaseModel):
    response: Any


class TokenRes(BaseRes):
    response: str


class TokenListRes(BaseRes):
    response: List[str]


class Credentials(BaseModel):
    username: str
    password: str

    _validate_username_1 = validator("username", allow_reuse=True)(
        custom_charset
    )
    _validate_username_2 = validator("username", allow_reuse=True)(
        starts_with("usr:")
    )


class NewUser(Credentials):
    fullname: Optional[str] = None


class NewInvitedUser(NewUser):
    invitation_code: str


class UserInfo(BaseModel):
    username: str
    fullname: Optional[str] = None
    organisation: Optional[str]
    level_of_access: int = 0

    _validate_username_1 = validator("username", allow_reuse=True)(
        custom_charset
    )
    _validate_username_2 = validator("username", allow_reuse=True)(
        starts_with("usr:")
    )


# class FullUserInfo(Credentials, UserInfo):
#     pass


class UserListResponse(BaseModel):
    response: List[UserInfo]


class MinimalInviteCode(BaseModel):
    organisation_id: str

    _validate_organisation_id_1 = validator(
        "organisation_id", allow_reuse=True
    )(custom_charset)
    _validate_organisation_id_2 = validator(
        "organisation_id", allow_reuse=True
    )(starts_with("org:"))


class InviteCode(MinimalInviteCode):
    code: str
    issuer_id: str
    num_registered: int


class InviteCodeListRes(BaseModel):
    response: List[InviteCode]


class UserUpdateUsername(BaseModel):
    new_username: str

    _validate_new_username_1 = validator("new_username", allow_reuse=True)(
        custom_charset
    )
    _validate_new_username_2 = validator("new_username", allow_reuse=True)(
        starts_with("usr:")
    )


class UserUpdateFullName(BaseModel):
    new_fullname: str


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
    name: Optional[str] = None

    _validate_organisation_id_1 = validator(
        "organisation_id", allow_reuse=True
    )(custom_charset)
    _validate_organisation_id_2 = validator(
        "organisation_id", allow_reuse=True
    )(starts_with("org:"))


class OrgListRes(BaseModel):
    response: List[MinimalOrganisation]


class Organisation(MinimalOrganisation):
    users: List[str]


class OrgUpdateOrgId(BaseModel):
    new_organisation_id: str

    _validate_new_organisation_id_1 = validator(
        "new_organisation_id", allow_reuse=True
    )(custom_charset)
    _validate_new_organisation_id_2 = validator(
        "new_organisation_id", allow_reuse=True
    )(starts_with("org:"))


class OrgUpdateName(BaseModel):
    new_name: str


# +------+
# | Docs |
# +------+


class DMEntityCreateBase(BaseModel):
    owner: str
    private: bool = False
    name: Optional[str] = None
    has_access: Optional[List[str]] = None


class DMEntityReadBase(DMEntityCreateBase):
    creator: str


class CreateDoc(DMEntityCreateBase):
    text: str
    author: Optional[str] = None
    created: Optional[datetime] = None
    tags: Optional[List[str]] = None


class ReadMinimalDoc(DMEntityReadBase):
    doc_id: str


class ReadDoc(ReadMinimalDoc):
    text: str
    author: Optional[str] = None
    created: Optional[datetime] = None
    tags: Optional[List[str]] = None


class ReadDocs(BaseModel):
    response: List[ReadMinimalDoc]


class CreateCorp(DMEntityCreateBase):
    include: List[str]


class ReadMinimalCorp(DMEntityReadBase):
    corpus_id: str


class ReadCorp(ReadMinimalCorp):
    includes: List[Union[ReadMinimalDoc, ReadMinimalCorp]]


class ReadCorps(BaseModel):
    response: List[ReadMinimalCorp]


class CreateDict(DMEntityCreateBase):
    words: List[str]


class ReadDict(DMEntityReadBase):
    dic_id: str
    words: List[str]


class ReadDicts(BaseModel):
    response: List[ReadDict]


class AnalyzeReq(BaseModel):
    entity_ids: List[str] = Field(
        ..., title="list of documents and corpuses to analyze",
    )


class AnalyzeRes(BaseModel):
    entity_id: str


class LexicsAnalyzeReq(AnalyzeReq):
    dicts: List[str]


class Spans(BaseModel):
    start_char: int
    end_char: int
    dictionary: str = Field(..., alias="dict")


class LexicsAnalyzePreRes(BaseModel):
    doc_id: str
    spans: List[Spans]


class LexicsAnalyzeRes(BaseModel):
    response: List[LexicsAnalyzePreRes]


class PredicatesAnalyzeReq(AnalyzeReq):
    argument: Optional[str] = None
    predicate: Optional[str] = None
    role: Optional[str] = None


class PredicatesAnalyzePreRes(AnalyzeRes):
    role: str
    predicate: str
    context: Optional[str] = None


class PredicatesAnalyzeRes(BaseModel):
    response: List[PredicatesAnalyzePreRes]


class StatsAnalyzeReq(AnalyzeReq):
    statistics: List[str]


# will be returned as values in a dict
class StatsAnalyzePreRes(AnalyzeRes):
    name: str
    unit: str
    value: Union[str, List[str], Dict[str, str]]


class StatsAnalyzeRes(BaseModel):
    """
    mapping from string key to stats about key object\n
    key can be either\n
    `all` for stats on whole set\n
    `corp:***` for stats about corpus (also a set of documents)\n
    `doc:***` for stats about document
    """

    response: Dict[str, StatsAnalyzePreRes]


class CompareAnalyzeReq(BaseModel):
    first_set: List[str]
    second_set: List[str]
    statistics: List[str]


class CompareAnalyzeRes(BaseModel):
    first_set: Dict[str, StatsAnalyzePreRes]
    second_set: Dict[str, StatsAnalyzePreRes]
    correlation: int
