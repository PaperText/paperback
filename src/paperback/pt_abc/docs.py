from abc import ABCMeta
from typing import Callable, ClassVar, NoReturn, Optional

from fastapi import APIRouter

from .base import Base, UserInfo

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

    def create_router(
        self,
        token: Callable[
            [Optional[int], Optional[int]], Callable[[str], UserInfo]
        ],
    ) -> APIRouter:
        router = APIRouter()

        @router.get(
            "/docs-test", tags=["docs"], response_model=str,
        )
        def test():
            return "success"

        return router
