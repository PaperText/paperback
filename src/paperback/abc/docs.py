from abc import ABCMeta
from typing import List, Callable, ClassVar, NoReturn, Optional

from fastapi import Body, APIRouter

from .base import Base
from .models import (
    Corpus,
    Document,
    UserInfo,
    Dictionary,
    TokenTester,
    MinimalCorpus,
    MinimalDocument,
    MinimalDictionary,
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
    """

    TYPE: ClassVar[str] = "DOCS"

    def create_router(self, token: TokenTester) -> APIRouter:
        router = APIRouter()

        # document access
        @router.get(
            "/docs",
            tags=["docs_module", "docs"],
            response_model=List[MinimalDocument],
        )
        def read_docs() -> List[MinimalDocument]:
            """
            returns list of all documents, accessible to user
            """
            return []

        @router.post("/doc", tags=["docs_module", "docs"])
        def create_doc(doc: Document):
            """
            creates document with given id if it's not occupied
            """
            return None

        @router.get(
            "/doc/{doc_id}",
            tags=["docs_module", "docs"],
            response_model=Document,
        )
        def read_doc(doc_id: str) -> Document:
            """
            returns document with given id if it exists
            """
            return None

        @router.put(
            "/doc/{doc_id}", tags=["docs_module", "docs"],
        )
        def update_doc(doc_id: str, doc: Document):
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
            response_model=List[MinimalCorpus],
        )
        def read_corps() -> List[MinimalCorpus]:
            """
            returns list of all corpuses, accessible to user
            """
            return []

        @router.post("/corp", tags=["docs_module", "corps"])
        def create_corp(corp: Corpus):
            """
            creates corpus with given id if it's not occupied
            """
            return None

        @router.get(
            "/corp/{corp_id}",
            tags=["docs_module", "corps"],
            response_model=Corpus,
        )
        def read_corp(corp_id: str) -> Corpus:
            """
            returns corpus with given id if it exists
            """
            return None

        @router.put(
            "/corp/{corp_id}", tags=["docs_module", "corps"],
        )
        def update_corp(corp_id: str, corp: Corpus):
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
            response_model=List[MinimalDictionary],
        )
        def read_dicts() -> List[MinimalDictionary]:
            """
            returns list of all dictionaries, accessible to user
            """
            return []

        @router.post("/dict", tags=["docs_module", "dict"])
        def create_dict(dict: Dictionary):
            """
            creates dictionaries with given id if it's not occupied
            """
            return None

        @router.get(
            "/dict/{dict_id}",
            tags=["docs_module", "dict"],
            response_model=Dictionary,
        )
        def read_dict(dict_id: str) -> Dictionary:
            """
            returns dictionaries with given id if it exists
            """
            return None

        @router.put(
            "/dict/{dict_id}", tags=["docs_module", "dict"],
        )
        def update_dict(dict_id: str, dict: Dictionary):
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
            response_model=str,
        )
        def analyze_lexics(entity_ids: List[str] = Body(...)):
            """
            analyzes lexics on list of given ids
            """
            return ""

        @router.post(
            "/analyze/markers",
            tags=["docs_module", "analyzer"],
            response_model=str,
        )
        def analyze_markers(entity_ids: List[str] = Body(...)):
            """
            analyzes markers on list of given ids
            """
            return ""

        @router.post(
            "/analyze/predicates",
            tags=["docs_module", "analyzer"],
            response_model=str,
        )
        def analyze_predicates(entity_ids: List[str] = Body(...)):
            """
            analyzes predicates on list of given ids
            """
            return ""

        @router.post(
            "/analyze/stats",
            tags=["docs_module", "analyzer"],
            response_model=str,
        )
        def analyze_stats(entity_ids: List[str] = Body(...)):
            """
            analyzes stats on list of given ids
            """
            return ""

        self.add_routes(router)
        return router
