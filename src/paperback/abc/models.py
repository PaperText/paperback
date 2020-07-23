from typing import (
    Any,
    Dict,
    List,
    Union,
    TypeVar,
    Callable,
    Optional,
    Protocol,
)
from datetime import datetime

from pydantic import Field, BaseModel


class BaseRes(BaseModel):
    response: Any


class TokenRes(BaseRes):
    response: str


class TokenListRes(BaseRes):
    response: List[str]


class Credentials(BaseModel):
    username: str
    password: str


class NewUser(Credentials):
    fullname: Optional[str] = None


class NewInvitedUser(NewUser):
    invitation_code: str


class UserInfo(BaseModel):
    username: str
    fullname: Optional[str] = None
    organisation: Optional[str]
    access_level: int = 0


# class FullUserInfo(Credentials, UserInfo):
#     pass


class UserListResponse(BaseModel):
    response: List[UserInfo]


class MinimalInviteCode(BaseModel):
    organisation: str


class InviteCode(BaseModel):
    code: str
    issuer_id: str
    organisation: str
    num_registered: int


class InviteCodeListRes(BaseModel):
    response: List[InviteCode]


class UserUpdateUsername(BaseModel):
    new_username: str


class UserUpdateFullName(BaseModel):
    new_fullname: str


class UserUpdatePassword(BaseModel):
    new_password: str


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
    org_id: str
    name: Optional[str] = None


class OrgListRes(BaseModel):
    response: List[MinimalOrganisation]


class Organisation(MinimalOrganisation):
    users: List[str]


class OrgUpdateOrgId(BaseModel):
    new_org_id: str


class OrgUpdateName(BaseModel):
    new_name: str


# +------+
# | Docs |
# +------+


class DMEntityCreateBase(BaseModel):
    owner: str
    private: bool = False
    name: Optional[str] = None


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
