from abc import ABCMeta, abstractmethod
from types import SimpleNamespace
from typing import Any, Dict, Callable, ClassVar, NoReturn, Optional
from pathlib import Path

from fastapi import APIRouter

from . import UserInfo


class Base(metaclass=ABCMeta):
    """
    base class for all modules of PaperText

    Attributes
    ----------
    TYPE: str
        type of module
    DEFAULTS: Dict[str, int]
        python dict of default values for configuration
    requires_dir: bool
        describes if directory for storage will be provide to __init__ call, default is `False`
    """

    TYPE: ClassVar[Optional[str]] = None
    DEFAULTS: ClassVar[Optional[Dict[str, Any]]] = None
    requires_dir: ClassVar[Optional[bool]] = None

    def __new__(cls, *args, **kwargs):
        """
        extends new to check for existence of specific fields in class instance
        """
        if cls.TYPE is None:
            raise ValueError(
                f"Class {cls} can't have class attribute "
                "`TYPE` as `None`, "
                "class should only inherit from `BaseMisc`, `BaseDocs` or `BaseAuth`"
            )
        if cls.DEFAULTS is None:
            raise NotImplementedError(
                f"Class {cls} can't have class attribute `DEFAULTS` as `None`"
            )
        if cls.requires_dir is None:
            raise NotImplementedError(
                f"Class {cls} can't have class attribute `requires_dir` as `None`"
            )
        instance = super().__new__(cls)
        return instance

    @abstractmethod
    def __init__(self, cfg: SimpleNamespace, storage_dir: Path):
        """
        constructor for all classes

        Parameters
        ----------
        cfg: dict
            python dict for accessing config
        storage_dir: Path
            pathlib object pointing to directory for module
        """
        raise NotImplementedError

    @abstractmethod
    def create_router(
        self,
        token: Callable[
            [Optional[int], Optional[int]], Callable[[str], UserInfo]
        ],
    ) -> APIRouter:
        """
        creates Router to mount to the main app

        should create `router` of type `fastapi.APIRouter`, call `self.add_routes` on router before return
        and return `router`
            ```self.router: APIRouter = APIRouter()
               ...
               self.add_routes(router)
               return router
            ```
        """
        raise NotImplementedError(
            "Unsupported class inheritance: cant inherit from `Base`"
        )

    def add_routes(self, router: APIRouter) -> NoReturn:
        """

        Parameters
        ----------
        router: APIRouter
            instance of APIRouter to add custom routes without redefining predefined self.create_router
        """
        pass
