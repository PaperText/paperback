from abc import ABCMeta
from typing import Any, Dict, List, Callable, ClassVar, NoReturn, Optional
from datetime import datetime

from fastapi import Body, Query, APIRouter

from .base import Base
from .models import *


class BaseDocs(Base, metaclass=ABCMeta):
    """
    base class for all text modules of PaperText

    Attributes
    ----------
    TYPE: str
        type of module
    DEFAULTS: Dict[str, int]
        python dict of default values for configuration
    requires_dir: bool
        describes if directory for storage will be provide to __init__ call
    """

    TYPE: ClassVar[str] = "DOCS"

    def create_router(self, token: TokenTester) -> APIRouter:
        router = APIRouter()

        # document access
        @router.get(
            "/docs", tags=["docs_module", "docs"], response_model=ReadDocs,
        )
        def read_docs(
            contains: Optional[str] = None,
            author: Optional[str] = None,
            created_before: Optional[datetime] = None,
            created_after: Optional[datetime] = None,
            tags: Optional[List[str]] = Query(None),
        ) -> ReadDocs:
            """
            returns list of all documents, accessible to user
            """
            return []

        @router.post("/doc", tags=["docs_module", "docs"])
        def create_doc(doc: CreateDoc):
            """
            creates document with given id if it's not occupied
            """
            return None

        @router.get(
            "/doc/{doc_id}",
            tags=["docs_module", "docs"],
            response_model=ReadDoc,
        )
        def read_doc(doc_id: str) -> ReadDoc:
            """
            returns document with given id if it exists
            """
            return None

        @router.put(
            "/doc/{doc_id}", tags=["docs_module", "docs"],
        )
        def update_doc(doc_id: str, doc: CreateDoc):
            """
            updates document with given id if it exists
            """
            return None

        @router.delete("/doc/{doc_id}", tags=["docs_module", "docs"])
        def delete_doc(doc_id: str):
            """
            deletes document with given id if it exists
            """
            return None

        # corpus management
        @router.get(
            "/corps",
            tags=["docs_module", "corps"],
            response_model=ReadCorps,
        )
        def read_corps() -> ReadCorps:
            """
            returns list of all corpuses, accessible to user
            """
            return []

        @router.post("/corp", tags=["docs_module", "corps"])
        def create_corp(corp: CreateCorp):
            """
            creates corpus with given id if it's not occupied
            """
            return None

        @router.get(
            "/corp/{corp_id}",
            tags=["docs_module", "corps"],
            response_model=ReadCorp,
        )
        def read_corp(corp_id: str) -> ReadCorp:
            """
            returns corpus with given id if it exists
            """
            return None

        @router.put(
            "/corp/{corp_id}", tags=["docs_module", "corps"],
        )
        def update_corp(corp_id: str, corp: CreateCorp):
            """
            updates corpus with given id if it exists
            """
            return None

        @router.delete(
            "/corp/{corp_id}", tags=["docs_module", "corps"],
        )
        def delete_corp(corp_id: str):
            """
            deletes corpus with given id if it exists
            """
            return None

        # dictionary management
        @router.get(
            "/dicts",
            tags=["docs_module", "dict"],
            response_model=ReadDicts,
        )
        def read_dicts() -> ReadDicts:
            """
            returns list of all dictionaries, accessible to user
            """
            return []

        @router.post("/dict", tags=["docs_module", "dict"])
        def create_dict(dict: CreateDict):
            """
            creates dictionaries with given id if it's not occupied
            """
            return None

        @router.get(
            "/dict/{dict_id}",
            tags=["docs_module", "dict"],
            response_model=ReadDict,
        )
        def read_dict(dict_id: str) -> ReadDict:
            """
            returns dictionaries with given id if it exists
            """
            return None

        @router.put(
            "/dict/{dict_id}", tags=["docs_module", "dict"],
        )
        def update_dict(dict_id: str, dict: CreateDict):
            """
            updates dictionaries with given id if it exists
            """
            return None

        @router.delete(
            "/dict/{dict_id}", tags=["docs_module", "dict"],
        )
        def delete_dict(dict_id: str):
            """
            deletes dictionaries with given id if it exists
            """
            return None

        # analyzer usage
        @router.post(
            "/analyze/lexics",
            tags=["docs_module", "analyzer"],
            response_model=LexicsAnalyzeRes,
        )
        def analyze_lexics(req: LexicsAnalyzeReq) -> LexicsAnalyzeRes:
            """
            analyzes lexics on list of given ids
            """
            return ""

        # @router.post(
        #     "/analyze/markers",
        #     tags=["docs_module", "analyzer"],
        #     response_model=str,
        # )
        # def analyze_markers(entity_ids: List[str] = Body(...)):
        #     """
        #     analyzes markers on list of given ids
        #     """
        #     return ""

        @router.post(
            "/analyze/predicates",
            tags=["docs_module", "analyzer"],
            response_model=PredicatesAnalyzeRes,
        )
        def analyze_predicates(
            request: PredicatesAnalyzeReq, return_context: bool = False
        ) -> PredicatesAnalyzeRes:
            """
            analyzes predicates on list of given ids
            """
            return ""

        @router.post(
            "/analyze/stats",
            tags=["docs_module", "analyzer"],
            response_model=StatsAnalyzeRes,
        )
        def analyze_stats(
            req: StatsAnalyzeReq, analyze_subcorps: bool = False
        ) -> StatsAnalyzeRes:
            """
            analyzes stats on list of given ids
            """
            return ""

        @router.post(
            "/analyze/compare",
            tags=["docs_module", "analyzer"],
            response_model=CompareAnalyzeRes,
        )
        def analyze_compare(
            req: CompareAnalyzeReq, analyze_subcorps: bool = False
        ) -> CompareAnalyzeRes:
            """
            analyzes stats on lists of given documents
            """
            return ""

        self.add_routes(router)
        return router
