from abc import ABCMeta, abstractmethod
from datetime import datetime
from enum import Enum
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Callable, ClassVar, Dict, Final, List, Optional

from fastapi import APIRouter, Body, Depends, Query

from .auth import BaseAuth
from .base import Base
from .models import (
    AvailableStats,
    CompareAnalyzeReq,
    CompareAnalyzeRes,
    CreateCorp,
    CreateDict,
    CreateDoc,
    LexicsAnalyzePreRes,
    LexicsAnalyzeReq,
    LexicsAnalyzeRes,
    PredicatesAnalyzePreRes,
    PredicatesAnalyzeReq,
    PredicatesAnalyzeRes,
    ReadCorp,
    ReadCorps,
    ReadDict,
    ReadDicts,
    ReadDoc,
    ReadDocs,
    ReadMinimalCorp,
    ReadMinimalDoc,
    StatsAnalyzePreRes,
    StatsAnalyzeReq,
    StatsAnalyzeRes,
    TokenTester,
    UserInfo,
)


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
    requires_auth: bool
        describes if Auth class will be provide to __init__ call
    """

    TYPE: Final = "DOCS"

    @abstractmethod
    def __init__(self, cfg: SimpleNamespace, storage_dir: Path, auth_module: BaseAuth):
        """
        constructor of new module

        Parameters
        ----------
        cfg : SimpleNamespace
            configuration of module. Can be accessed with dot(cfg.config) or braces(cfg["config"])
        storage_dir : Path
            folder for storing temporary files
        auth_module : BaseAuth
            instance of module, which is responsible for authentification
        """
        raise NotImplementedError

    # docs

    @abstractmethod
    async def create_doc(
        self,
        creator_id: str,
        creator_type: str,
        doc_id: str,
        text: str,
        analyzer_id: Optional["BaseDocs.AnalyzerEnum"] = None,
        private: bool = False,
        parent_corp_id: Optional[str] = None,
        name: Optional[str] = None,
        has_access: Optional[List[str]] = None,
        author: Optional[str] = None,
        created: Optional[datetime] = None,
        tags: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        create doc with specified parameters

        Parameters
        ----------
        creator_id : str
            id of user, who issued request for creation
        creator_type : str
            type of user, who issued request for creation
        doc_id: str
            id of corpus to read
        text : str
            text of the document
        analyzer_id : AnalyzerEnum, optional
            id of analyzer to use
        private: bool, optional
            new private info. default is False
        parent_corp_id: str, optional
            new parent corpus, specified by it's id. default is None
        name: str, optional
            new name of corpus. default is None
        has_access: List[str], optional
            list of people who have access to corpus. default is None
        author: str, optional
            author of the text. default is None
        created: datetime, optional
            date when text was created. default is None
        tags: str, optional
            optional list of tags. default is None

        Returns
        -------
        Dict[str, Any]
        """
        raise NotImplementedError

    @abstractmethod
    async def read_docs(
        self,
        requester_id: str,
        contains: Optional[str] = None,
        author: Optional[str] = None,
        created_before: Optional[datetime] = None,
        created_after: Optional[datetime] = None,
        tags: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """
        search for document with specified parameters

        Parameters
        ----------
        contains : str, optional
            search string. default is None
        author : str, optional
            author of text. default is None
        created_before : datetime, optional
            date before which the text was created. default is None
        created_after : datetime, optional
            date after which the text was created. default is None
        tags : List[str], optional
            list of tags, that must be in text. default is None

        Returns
        -------
        List[Dict[str, Any]]
            List of documents
        """
        raise NotImplementedError

    @abstractmethod
    async def read_doc(
        self,
        doc_id: str,
    ) -> Dict[str, Any]:
        """
        read document with specified id

        Parameters
        ----------
        doc_id : str
            id of document to read info about

        Returns
        -------
        Dict[str, Any]
            info about document
        """
        raise NotImplementedError

    @abstractmethod
    async def update_doc(
        self,
        doc_id: str,
        owner_id: Optional[str] = None,
        owner_type: Optional[str] = None,
        parent_corp_id: Optional[str] = None,
        text: Optional[str] = None,
        private: Optional[bool] = False,
        name: Optional[str] = None,
        has_access: Optional[List[str]] = None,
        author: Optional[str] = None,
        created: Optional[datetime] = None,
        tags: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        create doc with specified parameters

        Parameters
        ----------
        doc_id: str
            id of corpus to read
        owner_id : str, optional
            id of new user, who owns this document. default is None
        owner_type : str, optional
            type of new user, who owns this document. default is None
        parent_corp_id: str, optional
            new parent corpus, specified by it's id. default is None
        text : str, optional
            new text of the document. default is None
        private: bool, optional
            new private info. default is False
        name: str, optional
            new name of corpus. default is None
        has_access: List[str], optional
            list of people who have access to corpus. default is None
        author: str, optional
            author of the text. default is None
        created: datetime, optional
            date when text was created. default is None
        tags: str, optional
            optional list of tags. default is None

        Returns
        -------
        Dict[str, Any]
        """
        raise NotImplementedError

    @abstractmethod
    async def delete_doc(
        self,
        doc_id: str,
    ):
        """
        delete document with specified id

        Parameters
        ----------
        doc_id : str
            id of document to delete
        """
        raise NotImplementedError

    # corpuses

    @abstractmethod
    async def create_corp(
        self,
        issuer_id: str,
        issuer_type: str,
        corp_id: str,
        name: Optional[str] = None,
        parent_corp_id: Optional[str] = None,
        private: bool = False,
        has_access: Optional[List[str]] = None,
        to_include: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        create corpus with specified parameters

        Parameters
        ----------
        issuer_id : str
            id of user, who issued request for creation
        issuer_type : str
            type of user, who issued request for creation
        corp_id: str
            id of corpus to read
        name: str, optional
            new name of corpus. default is None
        parent_corp_id: str, optional
            new parent corpus, specified by it's id. default is None
        private: bool, optional
            new private info. default is False
        has_access: List[str], optional
            list of people who have access to corpus. default is None
        to_include: List[str], optional
            list of sub entities. default is None

        Returns
        -------
        Dict[str, Any]
        """
        if to_include is None:
            to_include = []
        raise NotImplementedError

    @abstractmethod
    async def read_corps(
        self,
        requester_id: str,
    ) -> List[Dict[str, Any]]:
        """
        read corpuses of specified user

        Parameters
        ----------
        requester_id: str
            id of user to get corpuses of

        Returns
        -------
        List[Dict[str, Any]]
        """
        raise NotImplementedError

    @abstractmethod
    async def read_corp(
        self,
        corp_id: str,
    ) -> Dict[str, Any]:
        """
        read corpus with specified id

        Parameters
        ----------
        corp_id: str
            id of corpus to read

        Returns
        -------
        Dict[str, Any]
        """
        raise NotImplementedError

    @abstractmethod
    async def update_corp(
        self,
        corp_id: str,
        name: Optional[str] = None,
        parent_corp_id: Optional[str] = None,
        private: bool = False,
        has_access: Optional[List[str]] = None,
        to_include: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        update corpus with specified id and specified info

        Parameters
        ----------
        corp_id: str
            id of corpus to read
        name: str, optional
            new name of corpus. default is None
        parent_corp_id: str, optional
            new parent corpus, specified by it's id. default is None
        private: bool, optional
            new private info. default is False
        has_access: List[str], optional
            list of people who have access to corpus. default is None
        to_include: List[str], optional
            list of sub entities. default is None

        Returns
        -------
        Dict[str, Any]
        """
        pass

    @abstractmethod
    async def delete_corp(self, corp_id: str):
        """
        delete corpus with specified id

        Parameters
        ----------
        corp_id: str
            id of corpus to delete
        """
        raise NotImplementedError

    def create_router(self, token_tester: TokenTester) -> APIRouter:
        router = APIRouter()

        # document access
        @router.post("/docs", tags=["docs_module", "docs"])
        async def create_doc(
            doc: CreateDoc[str],
            requester: UserInfo = Depends(token_tester(greater_or_equal=0)),
        ):
            """
            creates document with given id if it's not occupied
            """
            return await self.create_doc(
                creator_id=requester.user_id, creator_type="user", **dict(doc)
            )

        @router.get(
            "/docs",
            tags=["docs_module", "docs"],
            response_model=ReadDocs,
        )
        async def read_docs(
            requester: UserInfo = Depends(token_tester(greater_or_equal=0)),
            contains: Optional[str] = None,
            author: Optional[str] = None,
            created_before: Optional[datetime] = None,
            created_after: Optional[datetime] = None,
            tags: Optional[List[str]] = Query(None),
        ) -> ReadDocs:
            """
            returns list of all documents, accessible to user
            """
            raw_docs: List[Dict[str, Any]] = await self.read_docs(
                requester_id=requester.user_id,
                contains=contains,
                author=author,
                created_before=created_before,
                created_after=created_after,
                tags=tags,
            )
            return ReadDocs(response=[ReadMinimalDoc(**doc) for doc in raw_docs])

        @router.get(
            "/docs/{doc_id}",
            tags=["docs_module", "docs"],
            response_model=ReadDoc,
        )
        async def read_doc(doc_id: str) -> ReadDoc:
            """
            returns document with given id if it exists
            """
            return ReadDoc(**(await self.read_doc(doc_id)))

        @router.put(
            "/docs/{doc_id}",
            tags=["docs_module", "docs"],
        )
        async def update_doc(doc_id: str, doc: CreateDoc):
            """
            updates document with given id if it exists
            """
            return await self.update_doc(
                doc_id=doc_id,
                **dict(doc),
            )

        @router.delete("/docs/{doc_id}", tags=["docs_module", "docs"])
        async def delete_doc(doc_id: str):
            """
            deletes document with given id if it exists
            """
            return await self.delete_doc(doc_id)

        # corpus management
        @router.post("/corps", tags=["docs_module", "corps"])
        async def create_corp(
            corp: CreateCorp,
            requester: UserInfo = Depends(token_tester(greater_or_equal=0)),
        ):
            """
            creates corpus with given id if it's not occupied
            """
            return await self.create_corp(
                issuer_id=requester.user_id, issuer_type="user", **dict(corp)
            )

        @router.get(
            "/corps",
            tags=["docs_module", "corps"],
            response_model=ReadCorps,
        )
        async def read_corps(
            requester: UserInfo = Depends(token_tester(greater_or_equal=0)),
        ) -> ReadCorps:
            """
            returns list of all corpuses, accessible to user
            """
            raw_corpuses: List[Dict[str, Any]] = await self.read_corps(
                requester_id=requester.user_id
            )
            return ReadCorps(
                response=[ReadMinimalCorp(**corp) for corp in raw_corpuses]
            )

        @router.get(
            "/corps/{corp_id}",
            tags=["docs_module", "corps"],
            response_model=ReadCorp,
        )
        async def read_corp(corp_id: str) -> ReadCorp:
            """
            returns corpus with given id if it exists
            """
            return ReadCorp(**(await self.read_corp(corp_id=corp_id)))

        @router.put(
            "/corps/{corp_id}",
            tags=["docs_module", "corps"],
        )
        async def update_corp(corp_id: str, corp: CreateCorp):
            """
            updates corpus with given id if it exists
            """
            return await self.update_corp(
                corp_id=corp_id,
                **dict(corp),
            )

        @router.delete(
            "/corps/{corp_id}",
            tags=["docs_module", "corps"],
        )
        async def delete_corp(corp_id: str):
            """
            deletes corpus with given id if it exists
            """
            return await self.delete_corp(corp_id)

        # dictionary management
        @router.post("/dicts", tags=["docs_module", "dict"])
        async def create_dict(dict: CreateDict):
            """
            creates dictionaries with given id if it's not occupied
            """
            return None

        @router.get(
            "/dicts",
            tags=["docs_module", "dict"],
            response_model=ReadDicts,
        )
        async def read_dicts() -> ReadDicts:
            """
            returns list of all dictionaries, accessible to user
            """
            return []

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
            "/dicts/{dict_id}",
            tags=["docs_module", "dict"],
        )
        async def update_dict(dict_id: str, dict: CreateDict):
            """
            updates dictionaries with given id if it exists
            """
            return None

        @router.delete(
            "/dicts/{dict_id}",
            tags=["docs_module", "dict"],
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

        self.add_routes(router, token_tester)
        return router
