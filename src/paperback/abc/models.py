from typing import Any, Dict, List, Union, Callable, Optional, Protocol
from datetime import datetime

from pydantic import Field, BaseModel


class Credentials(BaseModel):
    username: str
    password: str


class NewUser(Credentials):
    fullname: Optional[str] = None


class NewInvitedUser(NewUser):
    invitation_code: str


class MinimalUserInfo(BaseModel):
    username: str
    fullname: Optional[str] = None


class UserInfo(MinimalUserInfo):
    organisation: Optional[str]
    access_level: int = 0


class FullUserInfo(Credentials, UserInfo):
    pass


class MinimalInviteCode(BaseModel):
    docs: List[str] = []
    organisation: Optional[str]


class InviteCode(BaseModel):
    code: str
    issuer_id: str
    organisation: str


class FullInviteCode(InviteCode):
    docs: List[str] = []


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


class OrgUpdateOrgId(BaseModel):
    new_org_id: str


class OrgUpdateName(BaseModel):
    new_name: str


class MinimalOrganisation(BaseModel):
    org_id: str
    name: Optional[str] = None


class Organisation(MinimalOrganisation):
    users: List[str]


class MinimalDocument(BaseModel):
    name: Optional[str] = None
    doc_id: str
    private: bool = False


MetaData = Dict[str, Union[str, List[str], Dict[str, str]]]


class Document(MinimalDocument):
    text: str
    author: Optional[str] = None
    created: Optional[datetime] = None
    metadata: Optional[MetaData] = None
    private: bool = False


class FullDocument(Document):
    creator_id: str


class MinimalCorpus(BaseModel):
    """
    minimal information about corpus,
    used as child corpus when reading parent corpus
    """

    name: Optional[str] = None
    corpus_id: str


class Corpus(MinimalCorpus):
    include: List[str]


class FullCorpus(MinimalCorpus):
    includes: List[Union[MinimalDocument, MinimalCorpus]]
    creator_id: str


class MinimalDictionary(BaseModel):
    name: Optional[str] = None
    dic_id: str


class Dictionary(MinimalDictionary):
    words: List[str]


class FullDictionary(Dictionary):
    creator_id: str


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
