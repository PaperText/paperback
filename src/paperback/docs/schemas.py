from __future__ import annotations

from pydantic import BaseModel, EmailStr, Field, UUID4


class CorpusBase(BaseModel):
    name: str

    parent_corpus_name: str | None = None


class CorpusCreate(CorpusBase):
    pass


class CorpusOut(CorpusBase):
    includes: list[DocOut | CorpusOut]


class Corpus(CorpusBase):
    corpus_uuid: UUID4

    includes: list[Doc | Corpus]

    class Config:
        orm_mode = True


class DocBase(BaseModel):
    name: str
    text: str

    corp_name: str | None = None

    tags: list[str] | None = None


class DocCreate(DocBase):
    parent_corp_name: str | None = None


class DocOut(DocBase):
    pass


class Doc(DocBase):
    doc_uuid: UUID4

    corpus: Corpus | None

    class Config:
        orm_mode = True


Corpus.update_forward_refs()
