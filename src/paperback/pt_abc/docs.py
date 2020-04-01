from typing import ClassVar, Callable, Optional, NoReturn

from fastapi import APIRouter

from .base import Base


class BaseDocs(Base):
    """
    base class for all text modules of PaperText

    Attributes
    ----------
    TYPE: str
        type of module
    DEFAULTS: Dict[str, int]
        python dict of default values for configuration
    """

    TYPE: ClassVar[str] = "DOCS"

    # def __init__(self, cfg: Mapping[str, Any]):
    # pass

    def create_router(
        self, token: Callable[[Optional[int], Optional[int]], Callable[[str], NoReturn]]
    ) -> APIRouter:
        pass
