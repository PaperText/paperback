from __future__ import annotations

from pydantic import BaseModel, EmailStr, Field, UUID4


class CorpusBase(BaseModel):
    name: str

    parent_corpus_name: str | None = None


class CorpusCreate(CorpusBase):
    pass


class CorpusOut(CorpusBase):
    includes: list[DocOut | CorpusOut]

    class Config:
        orm_mode = True


class Corpus(CorpusOut):
    corpus_uuid: UUID4

    includes: list[Doc | Corpus]


class DocBase(BaseModel):
    name: str
    text: str

    corp_name: str | None = None

    tags: list[str] | None = None


class DocCreate(DocBase):
    parent_corp_name: str | None = None


class DocOut(DocBase):
    class Config:
        orm_mode = True


class Doc(DocOut):
    doc_uuid: UUID4

    corpus: Corpus | None


Corpus.update_forward_refs()
