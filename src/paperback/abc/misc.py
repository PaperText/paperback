from abc import ABCMeta, abstractmethod
from types import SimpleNamespace
from typing import Dict, Callable, ClassVar, NoReturn, Optional
from pathlib import Path

from fastapi import APIRouter

from . import Base, BaseAuth, BaseDocs
from .models import UserInfo


class BaseMisc(Base, metaclass=ABCMeta):
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

    TYPE: ClassVar[Optional[str]] = "MISC"
    requires_auth: ClassVar[Optional[bool]]
    requires_docs: ClassVar[Optional[bool]]

    def __new__(cls, *args, **kwargs):
        """
        extends new to check for existence of specific fields in class instance
        """
        if not hasattr(cls, "requires_auth"):
            raise NotImplementedError(
                f"Class {cls} can't have class attribute `requires_auth` as `None`"
            )
        if not hasattr(cls, "requires_docs"):
            raise NotImplementedError(
                f"Class {cls} can't have class attribute `requires_docs` as `None`"
            )
        instance = super(Base, cls).__new__(cls)
        return instance

    @abstractmethod
    def __init__(
        self,
        cfg: SimpleNamespace,
        storage_dir: Path,
        auth: BaseAuth,
        docs: BaseDocs,
    ):
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
