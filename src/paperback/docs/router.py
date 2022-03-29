from fastapi import APIRouter, Depends
from py2neo import Transaction

from paperback.docs import crud, schemas
from paperback.docs.analyzers import (
    Analyzer,
    AnalyzerEnum,
    DEFAULT_ANALYZER,
    get_analyzer,
)
from paperback.docs.database import get_transaction
from paperback.docs.logging import logger
from paperback.docs.settings import get_docs_settings

docs_router = APIRouter()


@docs_router.on_event("startup")
async def startup():
    """
    Note
    ----
    this won't work in testing as id doesn't account overrides
    """
    settings = get_docs_settings()
    logger.debug("settings on startup of docs module: %s", settings)

    tx = next(get_transaction())

    if len(tx.graph.schema.get_uniqueness_constraints("Document")) == 0:
        tx.graph.schema.create_uniqueness_constraint("Document", "name")
    if len(tx.graph.schema.get_uniqueness_constraints("Corpus")) == 0:
        tx.graph.schema.create_uniqueness_constraint("Corpus", "name")


# docs
# ----


@docs_router.post("/docs", tags=["docs"], response_model=schemas.DocOut)
async def create_doc(
    doc: schemas.DocCreate,
    analyzer_id: AnalyzerEnum = DEFAULT_ANALYZER,
    get_analyzer=Depends(get_analyzer),
    tx: Transaction = Depends(get_transaction),
):
    """
    creates new document with specified info and returns it
    """
    analyzer = get_analyzer(analyzer_id)
    return crud.create_doc(tx, doc, analyzer_id, analyzer)


@docs_router.get("/docs", tags=["docs"], response_model=list[schemas.DocOut])
async def get_docs(
    tags: list[str] | None = None, tx: Transaction = Depends(get_transaction)
):
    """
    returns list of all documents
    """
    return crud.get_docs(tx, tags)


@docs_router.get("/docs/{name}", tags=["docs"], response_model=schemas.DocOut)
async def get_doc_by_name(
    name: str,
    tx: Transaction = Depends(get_transaction),
):
    """
    returns document with specified name
    """
    return crud.get_doc_by_name(tx, name)


@docs_router.patch(
    "/docs/{name}/tags/{tag}", tags=["docs"], response_model=schemas.DocOut
)
async def add_tag_to_doc_by_name(
    name: str,
    tag: str,
    tx: Transaction = Depends(get_transaction),
):
    """
    adds specefied tag to document with specified name
    """
    return crud.add_tag_to_doc_by_name(tx, name, tag)


@docs_router.delete(
    "/docs/{name}/tags/{tag}", tags=["docs"], response_model=schemas.DocOut
)
async def delete_tag_from_doc_by_name(
    name: str,
    tag: str,
    tx: Transaction = Depends(get_transaction),
):
    """
    removes specefied tag from document with specified name
    """
    return crud.delete_tag_from_doc_by_name(tx, name, tag)


@docs_router.delete("/docs/{name}", tags=["docs"])
async def delete_doc_by_name(
    name: str,
    tx: Transaction = Depends(get_transaction),
):
    """
    removes document with specified name
    """
    return crud.delete_doc_by_name(tx, name)


# corpus
# ------


@docs_router.post("/corp", tags=["corpus"], response_model=schemas.CorpusOut)
async def create_corpus(
    corp: schemas.CorpusCreate,
    tx: Transaction = Depends(get_transaction),
):
    """
    creates new corpus with specified info and returns it
    """
    return crud.create_corpus(tx, corp)


@docs_router.get("/corp", tags=["corpus"], response_model=list[schemas.CorpusOut])
async def get_corpuses(
    tx: Transaction = Depends(get_transaction),
):
    """
    returns list of all corpuses
    """
    return crud.get_corpuses(tx)


@docs_router.get("/corp/{name}", tags=["corpus"], response_model=schemas.CorpusOut)
async def get_corpus_by_name(name: str, tx: Transaction = Depends(get_transaction)):
    """
    returns corpus with specified name
    """
    return crud.get_corpus_by_name(tx, name)


@docs_router.patch("/corp/{name}/corp/{sub_name}", tags=["corpus"], response_model=schemas.CorpusOut)
async def add_subcorpus_to_corpus_by_name(
    name: str,
    sub_name: str,
    tx: Transaction = Depends(get_transaction)
):
    """
    adds a subcorpus with name `sub_name` to corpus with name `name`
    """
    return crud.add_subcorpus_to_corpus_by_name(tx, name, sub_name)


@docs_router.patch("/corp/{name}/docs/{sub_name}", tags=["corpus"], response_model=schemas.CorpusOut)
async def add_document_to_corpus_by_name(
    name: str,
    sub_name: str,
    tx: Transaction = Depends(get_transaction)
):
    """
    adds document with name `sub_name` to corpus with name `name`
    """
    return crud.add_document_to_corpus_by_name(tx, name, sub_name)


@docs_router.delete("/corp/{name}/corp/{sub_name}", tags=["corpus"], response_model=schemas.CorpusOut)
async def remove_subcorpus_from_corpus_by_name(
    name: str,
    sub_name: str,
    tx: Transaction = Depends(get_transaction)
):
    """
    removes subcorpus with name `sub_name` to corpus with name `name`
    """
    return crud.remove_subcorpus_from_corpus_by_name(tx, name, sub_name)


@docs_router.delete("/corp/{name}/docs/{sub_name}", tags=["corpus"], response_model=schemas.CorpusOut)
async def remove_document_from_corpus_by_name(
    name: str,
    sub_name: str,
    tx: Transaction = Depends(get_transaction)
):
    """
    removes document with name `sub_name` to corpus with name `name`
    """
    return crud.remove_document_from_corpus_by_name(tx, name, sub_name)


@docs_router.delete("/corp/{name}", tags=["corpus"])
async def delete_corpus_by_name(name: str, tx: Transaction = Depends(get_transaction)):
    """
    removes corpus with specified name
    """
    return crud.delete_corpus_by_name(tx, name)


# dicts
# -----
