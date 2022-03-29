from __future__ import annotations
from typing import Literal, TypedDict
from enum import Enum


from pydantic import BaseModel, EmailStr, Field, UUID4


# doc
# ---


class DocBase(BaseModel):
    name: str
    text: str

    tags: list[str] = []


class DocCreate(DocBase):
    pass


class DocOut(DocBase):
    pass


class Doc(DocBase):
    doc_uuid: UUID4

    class Config:
        orm_mode = True


# corp
# ----


class CorpusBase(BaseModel):
    name: str


class CorpusCreate(CorpusBase):
    pass


class CorpusOut(CorpusBase):
    includes: list[DocOut | CorpusOut]


class Corpus(CorpusBase):
    corpus_uuid: UUID4

    includes: list[Doc | Corpus]

    class Config:
        orm_mode = True


# dict
# ----


class DictionaryBase(BaseModel):
    name: str
    words: list[str] = []


class DictionaryCreate(DictionaryBase):
    pass


class DictionaryOut(DictionaryBase):
    pass


class Dictionary(DictionaryBase):
    dict_uuid: UUID4

    class Config:
        orm_mode = True


# analyzer
# --------


class DocOrCorp(str, Enum):
    doc = "doc"
    corp = "corp"

class DocsAndCorpuses(TypedDict):
    type: DocOrCorp
    name: str


class AnalyzeLexics(BaseModel):
    docs_and_corpuses: list[DocsAndCorpuses] = Field(..., description="list of documents and corpuses to analyze")
    dicts: list[str] = Field(..., description="list of dictionary names to use during analysis")


class AnalyzePredicates(BaseModel):
    docs_and_corpuses: list[DocsAndCorpuses] = Field(..., description="list of documents and corpuses to analyze")
    argument: str
    predicate: str
    role: str


class AnalyzeStats(BaseModel):
    docs_and_corpuses: list[DocsAndCorpuses] = Field(..., description="list of documents and corpuses to analyze")
    statistics: list[str]


class AnalyzeCompare(BaseModel):
    first_docs_and_corpuses: list[DocsAndCorpuses] = Field(..., description="first list of documents and corpuses to analyze")
    second_docs_and_corpuses: list[DocsAndCorpuses] = Field(..., description="second list of documents and corpuses to analyze")
    statistics: list[str]
