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


@docs_router.post("/docs", tags=["docs"], response_model=schemas.DocOut)
async def create_doc(
    doc: schemas.DocCreate,
    analyzer_id: AnalyzerEnum = DEFAULT_ANALYZER,
    get_analyzer=Depends(get_analyzer),
    tx: Transaction = Depends(get_transaction),
):
    """
    creates new document with specified info and return it
    """
    analyzer = get_analyzer(analyzer_id)
    return crud.create_doc(tx, doc, analyzer_id, analyzer)


@docs_router.get("/docs", tags=["docs"], response_model=list[schemas.DocOut])
async def get_docs(
    tags: list[str] | None = None, tx: Transaction = Depends(get_transaction)
):
    """
    returns list of all documents, accessible to user
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
