from __future__ import annotations

from datetime import datetime
from typing import List, Union, Callable, Optional, Protocol, Dict, Any

from pydantic import BaseModel


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


class Document(MinimalDocument):
    text: str
    author: Optional[str] = None
    created: Optional[datetime] = None
    metadata: Optional[Dict[Any, Any]] = None


class FullDocument(Document):
    creator_id: str


class MinimalCorpus(BaseModel):
    name: Optional[str] = None
    corpus_id: str


class Corpus(MinimalCorpus):
    create_with: List[str]


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
