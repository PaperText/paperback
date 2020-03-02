from abc import ABCMeta, abstractmethod
from typing import Dict, List, NoReturn, Tuple

from fastapi import APIRouter, FastAPI

from .base import Base


class BaseAuth(Base, metaclass=ABCMeta):
    """
    base class for all auth modules of PaperText

    Attributes
    ----------
    TYPE: str
        type of module
    DEFAULTS: Dict[str, int]
        python dict of default values for configuration
    """

    TYPE: str = "AUTH"

    @abstractmethod
    def create_user(
        self,
        email: str,
        password: str,
        name: str = "",
        organization: str = 0,
        access_level: int = 0,
    ) -> bool:
        """
        Creates user with declared parameters
        * Should meet these criteria:
            1. organization number should be the same
            2. level of access of tokens user should be grater or equal than 2
            3. level of access of created user should be
               equal or less than level of tokens user

        Parameters
        ----------
        email: string
            email of user to delete
        password: str
            password of user
        name: str, optional
            name of user
        organization: int
            organization of user
        access_level: int
            access_level of user

        Returns
        -------
        bool
            `True` if successful, `False` otherwise
        """
        raise NotImplementedError

    @abstractmethod
    def read_user(self, email: str) -> Dict[str, Tuple[str, int]]:
        """
        Get information about user with given email

        Parameters
        ----------
        email: string
            email of user to delete

        Returns
        -------
        dict with keywords
            name: str
                name of user
            organization: int
                organization of user
            access_level: int
                access_level of user
        """
        raise NotImplementedError

    @abstractmethod
    def update_user(
        self,
        email: str,
        password: str = None,
        name: str = None,
        organization: int = None,
        access_level: int = None,
    ) -> bool:
        """
        Updates user with given email

        Parameters
        ----------
        email: string
            email of user to delete
        password: str, optional
            password of user
        name: str, optional
            name of user to update to
        organization: int, optional
            organization of user to update to
        access_level: int, optional
            access_level of user to update to

        Returns
        -------
        bool
            `True` if successful, `False` otherwise
        """
        raise NotImplementedError

    @abstractmethod
    def delete_user(self, email: str) -> bool:
        """
        Removes user with given email

        Parameters
        ----------
        email: string
            email of user to delete

        Returns
        -------
        bool
            `True` if successful, `False` otherwise
        """
        raise NotImplementedError

    @abstractmethod
    def sign_in(self, email: str, password: str,) -> str:
        """
        checks email and password and returns new token

        Parameters
        ----------
        email: string
            email of user
        password: str
            password of user

        Returns
        -------
        str
            generated token
        """
        raise NotImplementedError

    @abstractmethod
    def sign_out(self,) -> bool:
        """
        removes token with which request was sent

        Returns
        -------
        bool
            `True` if successful, `False` otherwise
        """
        raise NotImplementedError

    @abstractmethod
    def sign_out_everywhere(self,) -> bool:
        """
        removes all tokens of current user

        Returns
        -------
        bool
            `True` if successful, `False` otherwise
        """
        raise NotImplementedError

    @abstractmethod
    def remove_token(self, token: str) -> bool:
        """
        removes token

        Parameters
        ----------
        token: str
            token to remove

        Returns
        -------
        bool
            `True` if successful, `False` otherwise
        """
        raise NotImplementedError

    @abstractmethod
    def remove_tokens(self, token: List[str]) -> bool:
        """
        removes tokens

        Parameters
        ----------
        token: List[str]
            list of tokens to remove

        Returns
        -------
        bool
            `True` if successful, `False` otherwise
        """
        raise NotImplementedError

    @abstractmethod
    def create_middleware(self, api: FastAPI, permissions: Dict[str, int]) -> NoReturn:
        """
        sets up middleware in main API

        Note
        ----
        very unsecured method, has access to whole API

        Parameters
        ----------
        api: FastAPI
            main instance of API
        permissions: Dict[str, int]
            permission to set in middleware
        """
        raise NotImplementedError

    def create_router(self) -> Tuple[APIRouter, Dict[Tuple[str, str], int]]:
        router = APIRouter()
        permissions = {}

        permissions[("GET", "/user")] = 0

        @router.get("/user")
        async def test():
            return ["test", "successful"]

        permissions[("POST", "/user")] = 0

        @router.post("/user")
        async def test():
            return ["test", "successful"]

        return router, permissions
