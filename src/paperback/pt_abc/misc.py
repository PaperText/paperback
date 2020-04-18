from abc import ABCMeta, abstractmethod
from pathlib import Path
from types import SimpleNamespace
from typing import Callable, ClassVar, Dict, NoReturn, Optional

from fastapi import APIRouter

from . import Base, BaseAuth, BaseDocs


class Misc(Base, metaclass=ABCMeta):
    """
    base class for all miscellaneous modules of PaperText

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
    requires_docs: bool
        weather docs will be provided to init
    """

    TYPE: ClassVar[str] = "MISC"
    requires_auth: ClassVar[bool] = False
    requires_docs: ClassVar[bool] = False

    @abstractmethod
    def __init__(self, cfg: SimpleNamespace, storage_dir: Path, auth: BaseAuth, docs: BaseDocs):
        """
        constructor for all classes

        Parameters
        ----------
        cfg: SimpleNamespace
            python dict for accessing config
        storage_dir: Path
            pathlib object, pointing to directory for module
        auth: BaseAuth
            auth module
        docs: BaseDocs
            docs module
        """
        raise NotImplementedError

    def create_router(
        self, token: Callable[[Optional[int], Optional[int]], Callable[[str], NoReturn]]
    ) -> APIRouter:
        """
        creates Router to mount to the main app
        """
        raise NotImplementedError
