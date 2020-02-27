from abc import ABCMeta, abstractmethod
from typing import Any, Dict, List, Tuple

# from fastapi import APIRouter


class BaseAuth(metaclass=ABCMeta):
    @abstractmethod
    def __init__(
        self, cfg: Dict[str, Any],
    ):
        """
        ABC or Auth module of paperback

        * db should be initialized here

        Parameters
        ----------
        cfg: dict
            python dict for accessing config
        """
        raise NotImplementedError

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
    def check_login_pass(self, email: str, password: str,) -> bool:
        """
        checks email and password

        Parameters
        ----------
        email: string
            email of user
        password: str
            password of user

        Returns
        -------
        bool
            `True` if successful, `False` otherwise
        """
        raise NotImplementedError

    @abstractmethod
    def login(self, email: str, password: str,) -> str:
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
    def logout(self,) -> bool:
        """
        removes token with which request was sent

        Returns
        -------
        bool
            `True` if successful, `False` otherwise
        """
        raise NotImplementedError

    @abstractmethod
    def logout_everywhere(self,) -> bool:
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
