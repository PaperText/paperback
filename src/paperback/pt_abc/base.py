from abc import ABCMeta, abstractmethod
from pathlib import Path
from types import SimpleNamespace
from typing import Callable, ClassVar, Dict, NoReturn, Optional

from fastapi import APIRouter


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

    TYPE: ClassVar[str]
    requires_dir: ClassVar[bool] = False

    def __new__(cls, *args, **kwargs):
        """
        modified new to add specific fields (only) to class instance
        """
        if not hasattr(cls, "DEFAULTS"):
            raise NotImplementedError("Class should have `DEFAULTS` as class attribute")
        instance = super(Base, cls).__new__(cls)
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
        self, token: Callable[[Optional[int], Optional[int]], Callable[[str], NoReturn]]
    ) -> APIRouter:
        """
        creates Router to mount to the main app
        """
        raise NotImplementedError
