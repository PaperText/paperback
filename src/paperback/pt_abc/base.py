from abc import ABCMeta, abstractmethod
from pathlib import Path
from types import SimpleNamespace
from typing import Callable, ClassVar, Dict, NoReturn, Optional

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

    TYPE: Optional[ClassVar[str]] = None
    requires_dir: Optional[ClassVar[bool]] = None

    def __new__(cls, *args, **kwargs):
        """
        extends new to check for existence of specific fields in class instance
        """
        if cls.TYPE is None:
            raise ValueError("Class can't have class attribute `TYPE` as `None`, "
                             "class should only inherit from `BaseMisc`, `BaseDocs` or `BaseAuth`")
        if cls.requires_dir is None:
            raise NotImplementedError("Class can't have class attribute `DEFAULTS` as `None`")
        if not hasattr(cls, "requires_dir"):
            raise NotImplementedError("Class can't have class attribute `requires_dir` as `None`")
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
        """
        raise NotImplementedError
