from __future__ import annotations

from typing import List, Union, Callable, Optional, Protocol

from pydantic import BaseModel

# allows to edclare self reference
# might be not needed rn or included in the future




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
    name: Optional[str] = None
    org_id: str


class Organisation(MinimalOrganisation):
    users: List[UserInfo]


class MinimalDocument(BaseModel):
    name: Optional[str] = None
    doc_id: str


class Document(MinimalDocument):
    creator_id: str
    text: str


class MinimalCorpus(BaseModel):
    name: Optional[str] = None
    corpus_id: str


class Corpus(MinimalCorpus):
    creator_id: str
    includes: List[Union[MinimalDocument, MinimalCorpus]]


class MinimalDictionary(BaseModel):
    name: Optional[str] = None
    dic_id: str


class Dictionary(MinimalDictionary):
    creator_id: str
    words: List[str]
