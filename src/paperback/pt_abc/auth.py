from abc import ABCMeta, abstractmethod
from pathlib import Path
from typing import Any, Callable, Dict, List, NoReturn, Tuple

from fastapi import APIRouter, Body, Depends, FastAPI, Header
from pydantic import BaseModel

from .base import Base


class Credentials(BaseModel):
    email: str
    password: str


class UserInfo(BaseModel):
    email: str
    organization: int = 0
    access_level: int = 0


class FullUser(Credentials, UserInfo):
    pass


class NewUser(FullUser):
    invitation_code: str


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
    def test_token(
        self, greater_or_equal: int, one_of: List[int]
    ) -> Callable[[Header], NoReturn]:
        """
        check is token is correct and if tokens loa is gte ml

        Parameters
        ----------
        greater_or_equal: int
            minimum loa, tokens loa should be `>=`
        one_of: List[str]
            list of loa, tokens load should be `loa in one_of`

        Returns
        -------
        Callable[[Header], NoReturn]
            FastAPIs dependency, which raises Exception
            #TODO: add Error for wrong token
        """
        raise NotImplementedError

    def create_router(
        self, token: Callable[[int], Callable[[Header], NoReturn]]
    ) -> APIRouter:
        router = APIRouter()

        @router.post("/signin", tags=["auth"])
        async def signin(user: Credentials):
            """
            generates new token if provided email and password are correct
            """
            return True

        @router.get("/signout", tags=["auth"])
        async def signout():
            """
            removes token from request
            """
            return True

        @router.get("/signout_everywhere", tags=["auth"])
        async def signout_everywhere():
            """
            removes all tokens, associated with tokens user
            """
            return True

        @router.post("/signup", tags=["auth"])
        async def signup(user: NewUser):
            """
            creates new user with provided email, password, organization, access_level and invitation code
            """
            return True

        @router.get("/users/me", tags=["user"])
        async def read_user():
            """
            return info about user, associated with user from token in request
            """
            return True

        @router.put("/users/me", tags=["user"])
        async def update_user(user: FullUser):
            """
            updates info of user, associated with user from token in request
            """
            return True

        @router.delete("/users/me", tags=["user"])
        async def delete_user(user: FullUser):
            """
            removes user, associated with user from token in request
            """
            return True

        @router.post("/users", tags=["user"])
        async def create_user(user: FullUser):
            """
            creates user with provided email, password, organization and access_level

            Note
            ----
            * only users with access level of 2 and more can use this function
            * users are created in the same organization as the requester
            """
            return True

        @router.get("/users/{user_email}", tags=["user"])
        async def read_users(user_email: str):
            """
            reads info about requested user
            """
            return user_email

        @router.put("/users/{user_email}", tags=["user"])
        async def update_users(user_email: str):
            """
            updates info about requested user
            """
            return user_email

        @router.delete("/users/{user_email}", tags=["user"])
        async def remove_users(user_email: str):
            """
            removes requested user
            """
            return user_email

        @router.delete("/token", tags=["token"])
        async def delete_token(token_identifier: str):
            """
            removes token by provided identifier: either token itself or token uuid
            """
            return token_identifier

        @router.get("/tokens", tags=["token"])
        async def get_tokens():
            """
            returns all tokens, associated with user from token in request
            """
            return True

        return router
