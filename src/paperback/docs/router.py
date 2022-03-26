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


@docs_router.get("/docs", tags=["docs"], response_model=list[schemas.DocOut])
async def get_docs(tx: Transaction = Depends(get_transaction)):
    """
    returns list of all documents, accessible to user
    """
    return crud.get_docs(tx)


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
