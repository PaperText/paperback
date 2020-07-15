from datetime import datetime
from typing import List, Union, Callable, Optional, Protocol, Dict, Any

from pydantic import BaseModel, Field


class Credentials(BaseModel):
    username: str
    password: str


class NewUser(Credentials):
    full_name: Optional[str] = None
    invitation_code: str


class UserInfo(BaseModel):
    username: str
    full_name: Optional[str] = None
    organization: str = "Public"
    access_level: int = 0


class FullUserInfo(Credentials, UserInfo):
    pass


class InviteCode(BaseModel):
    issuer_id: str
    code: str
    docs: List[str] = []


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


class Organisation(MinimalOrganisation):
    users: List[UserInfo]


class MinimalDocument(BaseModel):
    name: Optional[str] = None
    doc_id: str


MetaData = Dict[str, Union[str, List[str], Dict[str, str]]]


class Document(MinimalDocument):
    text: str
    author: Optional[str] = None
    created: Optional[datetime] = None
    metadata: Optional[MetaData] = None


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
        ...,
        title="list of documents and corpuses to analyze",
    )


class AnalyzeRes(BaseModel):
    entity_id: str


class LexicsAnalyzeReq(AnalyzeReq):
    dicts: List[str]


class Spans(BaseModel):
    start_char: int
    end_char: int
    dictionary: str = Field(..., alias="dict")


# will be returned in a List
class LexicsAnalyzeRes(BaseModel):
    doc_id: str
    spans: List[Spans]


class PredicatesAnalyzeReq(AnalyzeReq):
    argument: Optional[str] = None
    predicate: Optional[str] = None
    role: Optional[str] = None


# will be returned in a List
class PredicatesAnalyzeRes(AnalyzeRes):
    role: str
    predicate: str
    context: Optional[str] = None


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
