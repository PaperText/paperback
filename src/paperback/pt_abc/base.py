from abc import ABCMeta, abstractmethod
from typing import Any, Callable, ClassVar, Dict, Mapping, NoReturn, Optional

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
    """

    TYPE: ClassVar[str] = "MISC"

    def __new__(cls, *args, **kwargs):
        """
        modified new to add specific fields (only) to class instance
        """
        if not hasattr(cls, "DEFAULTS"):
            raise NotImplementedError("Class should have `DEFAULTS` as class attribute")
        instance = super(Base, cls).__new__(cls)
        return instance

    @abstractmethod
    def __init__(self, cfg: Mapping[str, Any]):
        """
        constructor for all classes

        Parameters
        ----------
        cfg: dict
            python dict for accessing config
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
