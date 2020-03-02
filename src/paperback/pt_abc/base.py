from abc import ABCMeta, abstractmethod
from typing import Any, Dict, NoReturn, Tuple

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

    TYPE: str = "MISC"

    def __new__(cls, *args, **kwargs):
        """
        modified new to add specific fields (only) to class instance
        """
        if not hasattr(cls, "DEFAULTS"):
            raise NotImplementedError("Class should have `DEFAULTS` as class attribute")
        instance = super(Base, cls).__new__(cls)
        return instance

    def __init__(self, cfg: Dict[str, Any]):
        """
        constructor for all classes

        Note
        ----
        DB connections should be created here

        Parameters
        ----------
        cfg: dict
            python dict for accessing config
        """
        raise NotImplementedError

    @abstractmethod
    def create_router(self) -> Tuple[APIRouter, Dict[Tuple[str, str], int]]:
        """
        creates Router to mount to the main app

        Note
        ----
        Router is already defined as `instance.ROUTER: APIRouter = APIRouter()`
        """
        raise NotImplementedError
