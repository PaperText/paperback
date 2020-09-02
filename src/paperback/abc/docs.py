from abc import ABCMeta, abstractmethod
from typing import Any, Dict, List, Callable, ClassVar, Optional
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

    @abstractmethod
    async def create_doc(
        self,
        doc_id: str,
        parent_corp_id: str,
        text: str,
        private: bool = False,
        name: Optional[str] = None,
        has_access: Optional[List[str]] = None,
        author: Optional[str] = None,
        created: Optional[datetime] = None,
        tags: Optional[List[str]] = None,
    ):
        raise NotImplementedError

    @abstractmethod
    async def read_docs(
        self,
        contains: Optional[str] = None,
        author: Optional[str] = None,
        created_before: Optional[datetime] = None,
        created_after: Optional[datetime] = None,
        tags: Optional[List[str]] = None,
    ):
        raise NotImplementedError

    @abstractmethod
    async def create_corp(
        self,
        corp_id: str,
        name: Optional[str] = None,
        parent_corp_id: Optional[str] = None,
        private: bool = False,
        has_access: Optional[List[str]] = None,
        to_include=None,
    ):
        if to_include is None:
            to_include = []
        raise NotImplementedError

    @abstractmethod
    async def read_corps(
        self,
        corp_id: str,
        name: Optional[str] = None,
        parent_corp_id: Optional[str] = None,
        private: bool = False,
        has_access: Optional[List[str]] = None,
        to_include=None,
    ):
        if to_include is None:
            to_include = []
        raise NotImplementedError

    def create_router(self, token: TokenTester) -> APIRouter:
        router = APIRouter()

        # document access
        @router.post("/docs", tags=["docs_module", "docs"])
        async def create_doc(doc: CreateDoc):
            """
            creates document with given id if it's not occupied
            """
            return await self.create_doc(**dict(doc))

        @router.get(
            "/docs", tags=["docs_module", "docs"], response_model=ReadDocs,
        )
        async def read_docs(
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

        @router.get(
            "/docs/{doc_id}",
            tags=["docs_module", "docs"],
            response_model=ReadDoc,
        )
        async def read_doc(doc_id: str) -> ReadDoc:
            """
            returns document with given id if it exists
            """
            return None

        @router.put(
            "/docs/{doc_id}", tags=["docs_module", "docs"],
        )
        async def update_doc(doc_id: str, doc: CreateDoc):
            """
            updates document with given id if it exists
            """
            return None

        @router.delete("/docs/{doc_id}", tags=["docs_module", "docs"])
        async def delete_doc(doc_id: str):
            """
            deletes document with given id if it exists
            """
            return None

        # corpus management
        @router.post("/corps", tags=["docs_module", "corps"])
        async def create_corp(corp: CreateCorp):
            """
            creates corpus with given id if it's not occupied
            """
            return await self.create_corp(**dict(corp))

        @router.get(
            "/corps", tags=["docs_module", "corps"], response_model=ReadCorps,
        )
        async def read_corps() -> ReadCorps:
            """
            returns list of all corpuses, accessible to user
            """
            return await self.read_corps()

        @router.get(
            "/corps/{corp_id}",
            tags=["docs_module", "corps"],
            response_model=ReadCorp,
        )
        async def read_corp(corp_id: str) -> ReadCorp:
            """
            returns corpus with given id if it exists
            """
            return None

        @router.put(
            "/corps/{corp_id}", tags=["docs_module", "corps"],
        )
        async def update_corp(corp_id: str, corp: CreateCorp):
            """
            updates corpus with given id if it exists
            """
            return None

        @router.delete(
            "/corps/{corp_id}", tags=["docs_module", "corps"],
        )
        async def delete_corp(corp_id: str):
            """
            deletes corpus with given id if it exists
            """
            return None

        # dictionary management
        @router.get(
            "/dicts", tags=["docs_module", "dict"], response_model=ReadDicts,
        )
        async def read_dicts() -> ReadDicts:
            """
            returns list of all dictionaries, accessible to user
            """
            return []

        @router.post("/dicts", tags=["docs_module", "dict"])
        async def create_dict(dict: CreateDict):
            """
            creates dictionaries with given id if it's not occupied
            """
            return None

        @router.get(
            "/dicts/{dict_id}",
            tags=["docs_module", "dict"],
            response_model=ReadDict,
        )
        async def read_dict(dict_id: str) -> ReadDict:
            """
            returns dictionaries with given id if it exists
            """
            return None

        @router.put(
            "/dicts/{dict_id}", tags=["docs_module", "dict"],
        )
        async def update_dict(dict_id: str, dict: CreateDict):
            """
            updates dictionaries with given id if it exists
            """
            return None

        @router.delete(
            "/dicts/{dict_id}", tags=["docs_module", "dict"],
        )
        async def delete_dict(dict_id: str):
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
        async def analyze_lexics(req: LexicsAnalyzeReq) -> LexicsAnalyzeRes:
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
        async def analyze_predicates(
            request: PredicatesAnalyzeReq, return_context: bool = False
        ) -> PredicatesAnalyzeRes:
            """
            analyzes predicates on list of given ids
            """
            return ""

        @router.get(
            "/analyze/available_stats",
            tags=["docs_module", "analyzer"],
            response_model=AvailableStats,
        )
        async def available_stats() -> StatsAnalyzeRes:
            """
            list of available stats
            """
            return []

        @router.post(
            "/analyze/stats",
            tags=["docs_module", "analyzer"],
            response_model=StatsAnalyzeRes,
        )
        async def analyze_stats(
            req: StatsAnalyzeReq, analyze_sub_entities: bool = False
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
        async def analyze_compare(
            req: CompareAnalyzeReq, analyze_subcorps: bool = False
        ) -> CompareAnalyzeRes:
            """
            analyzes stats on lists of given documents
            """
            return ""

        self.add_routes(router)
        return router
