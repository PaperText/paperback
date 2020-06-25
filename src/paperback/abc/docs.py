from abc import ABCMeta
from typing import Callable, ClassVar, NoReturn, Optional, List

from fastapi import APIRouter, Body

from .base import Base
from .models import UserInfo, TokenTester


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
            "/docs", tags=["docs"], response_model=List[str],
        )
        def read_docs() -> List[str]:
            """
            returns list of all documents, accessible to user
            """
            return []

        @router.post(
            "/doc", tags=["docs"], response_model=str,
        )
        def create_doc(doc: str):
            """
            creates document with given id if it's not occupied
            """
            return ""

        @router.get(
            "/doc/{doc_id}", tags=["docs"], response_model=str,
        )
        def read_doc(doc_id: str) -> str:
            """
            returns document with given id if it exists
            """
            return ""

        @router.put(
            "/doc/{doc_id}", tags=["docs"], response_model=str,
        )
        def update_doc(doc_id: str, doc: str):
            """
            updates document with given id if it exists
            """
            return ""

        @router.delete(
            "/doc/{doc_id}", tags=["docs"], response_model=str,
        )
        def delete_doc(doc_id: str):
            """
            deletes document with given id if it exists
            """
            return ""

        # corpus management
        @router.get(
            "/corps", tags=["docs", "corps"], response_model=List[str],
        )
        def read_corps() -> List[str]:
            """
            returns list of all corpuses, accessible to user
            """
            return []

        @router.post(
            "/corp", tags=["docs", "corps"], response_model=str,
        )
        def create_corp(corp: str):
            """
            creates corpus with given id if it's not occupied
            """
            return ""

        @router.get(
            "/corp/{corp_id}", tags=["docs", "corps"], response_model=str,
        )
        def read_corp(corp_id: str) -> str:
            """
            returns corpus with given id if it exists
            """
            return ""

        @router.put(
            "/corp/{corp_id}", tags=["docs", "corps"], response_model=str,
        )
        def update_corp(corp_id: str, corp: str):
            """
            updates corpus with given id if it exists
            """
            return ""

        @router.delete(
            "/corp/{corp_id}", tags=["docs", "corps"], response_model=str,
        )
        def delete_corp(corp_id: str):
            """
            deletes corpus with given id if it exists
            """
            return ""

        # dictionary management
        @router.get(
            "/dicts", tags=["docs", "dicts"], response_model=List[str],
        )
        def read_dicts() -> List[str]:
            """
            returns list of all dictionaries, accessible to user
            """
            return []

        @router.post(
            "/dict", tags=["docs", "dicts"], response_model=str,
        )
        def create_dict(dict: str):
            """
            creates dictionaries with given id if it's not occupied
            """
            return ""

        @router.get(
            "/dict/{dict_id}", tags=["docs", "dicts"], response_model=str,
        )
        def read_dict(dict_id: str) -> str:
            """
            returns dictionaries with given id if it exists
            """
            return ""

        @router.put(
            "/dict/{dict_id}", tags=["docs", "dicts"], response_model=str,
        )
        def update_dict(dict_id: str, dict: str):
            """
            updates dictionaries with given id if it exists
            """
            return ""

        @router.delete(
            "/dict/{dict_id}", tags=["docs", "dicts"], response_model=str,
        )
        def delete_dict(dict_id: str):
            """
            deletes dictionaries with given id if it exists
            """
            return ""

        # analyzer usage
        @router.post(
            "/analyze/lexics",
            tags=["docs", "analyzer"],
            response_model=str,
        )
        def analyze_lexics(entity_ids: List[str] = Body(...)):
            """
            analyzes lexics on list of given ids
            """
            return ""

        @router.post(
            "/analyze/markers",
            tags=["docs", "analyzer"],
            response_model=str,
        )
        def analyze_markers(entity_ids: List[str] = Body(...)):
            """
            analyzes markers on list of given ids
            """
            return ""

        @router.post(
            "/analyze/predicates",
            tags=["docs", "analyzer"],
            response_model=str,
        )
        def analyze_predicates(entity_ids: List[str] = Body(...)):
            """
            analyzes predicates on list of given ids
            """
            return ""

        @router.post(
            "/analyze/stats",
            tags=["docs", "analyzer"],
            response_model=str,
        )
        def analyze_stats(entity_ids: List[str] = Body(...)):
            """
            analyzes stats on list of given ids
            """
            return ""

        self.add_routes(router)
        return router
