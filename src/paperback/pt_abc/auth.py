from abc import ABCMeta, abstractmethod
from pathlib import Path
from typing import Any, Callable, Dict, List, NoReturn, Tuple, Mapping, ClassVar

from fastapi import APIRouter, Body, Depends, FastAPI, Header
from pydantic import BaseModel

from ..exceptions import TokenException
from .base import Base


class Credentials(BaseModel):
    username: str
    password: str


class UserInfo(BaseModel):
    username: str
    organization: str = "Public"
    access_level: int = 0


class FullUser(Credentials, UserInfo):
    pass


class NewUser(FullUser):
    invitation_code: str


class Token(BaseModel):
    token: str


class Tokens(BaseModel):
    tokens: List[str]


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

    TYPE: ClassVar[str] = "AUTH"

    @abstractmethod
    def __init__(self, cfg: Mapping[str, Any], keys_dir: Path):
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
    def create_user(
        self,
        username: str,
        password: str,
        access_level: int = 0,
        organization: str = "Public",
    ):
        """
        Creates user with declared parameters
        * Should meet these criteria:
            1. organization number should be the same
            2. level of access of tokens user should be grater or equal than 2
            3. level of access of created user should be
               equal or less than level of tokens user

        Parameters
        ----------
        username: string
            username of user to delete
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
    def read_user(self, username: str) -> Dict[str, Tuple[str, int]]:
        """
        Get information about user with given username

        Parameters
        ----------
        username: string
            username of user to delete

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
        username: str,
        password: str = None,
        name: str = None,
        access_level: int = None,
        organization: str = None,
    ) -> bool:
        """
        Updates user with given username

        Parameters
        ----------
        username: string
            username of user to delete
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
    def delete_user(self, username: str) -> bool:
        """
        Removes user with given username

        Parameters
        ----------
        username: string
            username of user to delete

        Returns
        -------
        bool
            `True` if successful, `False` otherwise
        """
        raise NotImplementedError

    @abstractmethod
    def sign_in(self, username: str, password: str,) -> str:
        """
        checks username and password and returns new token

        Parameters
        ----------
        username: string
            username of user
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
    def sign_up(self, user: NewUser) -> str:
        """
        creates new user with given info if invite code exists

        Parameters
        ----------
        user: NewUser
            info about new user

        Returns
        -------
        str
            generated token
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
    def add_CORS(self, api: FastAPI) -> NoReturn:
        """
        adds CORS policy to api

        Parameters
        ----------
        api: FastAPI
            instance of api
        """
        raise NotImplementedError

    @abstractmethod
    def test_token(self, greater_or_equal: int, one_of: List[int]) -> bool:
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
        bool
            returns `True` if token is active and
        """
        raise NotImplementedError

    def token(
        self, greater_or_equal: int = None, one_of: List[int] = None
    ) -> Callable[[List[str]], NoReturn]:
        if not greater_or_equal and not one_of:
            raise ValueError("either greater_or_equal or one_of should be set")

        def fn(authorization: str = Header(...)) -> NoReturn:
            if not self.test_token(greater_or_equal, one_of):
                raise TokenException(name=authorization)

        return fn

    def create_router(
        self, token: Callable[[int], Callable[[Header], NoReturn]]
    ) -> APIRouter:
        router = APIRouter()

        @router.get(
            "/test", tags=["test"], dependencies=[Depends(token(greater_or_equal=2))]
        )
        async def tststs():
            """
            test
            """
            return True

        @router.post("/signin", tags=["auth"], response_model=Token)
        async def signin(user: Credentials):
            """
            generates new token if provided username and password are correct
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

        @router.post("/signup", tags=["auth"], response_model=Token)
        async def signup(user: NewUser):
            """
            creates new user with provided username, password, organization, access_level and invitation code
            """
            return True

        @router.get("/users/me", tags=["user"], response_model=UserInfo)
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
        async def create_users(user: FullUser):
            """
            creates user with provided username, password, organization and access_level

            Note
            ----
            * only users with access level of 2 and more can use this function
            * users are created in the same organization as the requester
            """
            await self.create_user(user.username, user.password, user.access_level, user.organization)


        @router.get("/users/{user_username}", tags=["user"], response_model=UserInfo)
        async def read_users(user_username: str):
            """
            reads info about requested user
            """
            return user_username

        @router.put("/users/{user_username}", tags=["user"])
        async def update_users(user_username: str):
            """
            updates info about requested user
            """
            return user_username

        @router.delete("/users/{user_username}", tags=["user"])
        async def remove_users(user_username: str):
            """
            removes requested user
            """
            return user_username

        @router.delete("/token", tags=["token"])
        async def delete_token(token_identifier: str):
            """
            removes token by provided identifier: either token itself or token uuid
            """
            return token_identifier

        @router.get("/tokens", tags=["token"], response_model=Tokens)
        async def get_tokens():
            """
            returns all tokens, associated with user from token in request
            """
            return True

        return router
