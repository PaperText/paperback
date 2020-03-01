from abc import ABCMeta, abstractmethod
from typing import Any, Dict

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
    PERMISSIONS: Dict[str, Any]
        python dict of routes and minimum required access level
    ROUTER: APIRouter
        instance of Fastapi.APIRouter
    """

    TYPE: str = "MISC"

    def __new__(cls, *args, **kwargs):
        """
        modified new to add specific fields (only) to class instance
        """
        instance = super(Base, cls).__new__(cls)
        instance.DEFAULTS: Dict[str, int] = {}
        instance.PERMISSIONS: Dict[str, Any] = {}
        instance.ROUTER: APIRouter = APIRouter()
        return instance

    def __init__(
        self, cfg: Dict[str, Any],
    ):
        """
        constructor for all modules

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
    def create_router(self) -> APIRouter:
        """
        creates Router to mount to the main app

        Note
        ----
        Router is already defined as `instance.ROUTER: APIRouter = APIRouter()`
        """
        raise NotImplementedError
