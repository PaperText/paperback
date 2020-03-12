from typing import ClassVar, Callable, NoReturn, Mapping, Any

from fastapi import Header, APIRouter

from .base import Base


class BaseTexts(Base):
    TYPE: ClassVar[str] = "TEXTS"

    def __init__(self, cfg: Mapping[str, Any]):
        # super().__init__(cfg)
        pass

    def create_router(self, token: Callable[[int], Callable[[Header], NoReturn]]) -> APIRouter:
        pass
