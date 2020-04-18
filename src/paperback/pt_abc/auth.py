from abc import ABCMeta, abstractmethod
from typing import Callable, ClassVar, Dict, List, NoReturn, Optional

from fastapi import APIRouter, Depends, FastAPI, Header
from pydantic import BaseModel

from .base import Base
from ..exceptions import TokenException


class Credentials(BaseModel):
    username: str
    password: str


class UserInfo(BaseModel):
    username: str
    full_name: Optional[str] = None
    organization: str = "Public"
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
    requires_dir: bool
        describes if directory for storage will be provide to __init__ call
    """

    TYPE: ClassVar[str] = "AUTH"

    @abstractmethod
    async def add_CORS(self, api: FastAPI) -> NoReturn:
        """
        adds CORS policy to api

        Parameters
        ----------
        api: FastAPI
            instance of api
        """
        raise NotImplementedError

    @abstractmethod
    async def get_user_from_token(self) -> UserInfo:
        """
        decodes and validates token, returning user from token in "Auth" header

        Returns
        -------
        UserInfo (instance with those attributes)
            username: str
                username of user
            name: str
                name of user
            organization: str
                organization of user
            access_level: int
                access_level of user

        """

    @abstractmethod
    async def test_token(
        self, greater_or_equal: Optional[int] = None, one_of: Optional[List[int]] = None
    ) -> bool:
        """
        check if token is correct and if tokens suits parameters

        validates tokens fields and checks that access level is
            * access_level >= greater_or_equal if greater_or_equal is non None, and
            * if access_level exists ib one_of if one_of is not None

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
        self, greater_or_equal: Optional[int] = None, one_of: Optional[List[int]] = None
    ) -> Callable[[str], NoReturn]:
        if not greater_or_equal and not one_of:
            raise ValueError("either greater_or_equal or one_of should be set")

        def fn(authorization: str = Header(...)) -> NoReturn:
            if not self.test_token(greater_or_equal, one_of):
                raise TokenException(token=authorization)

        return fn

    @abstractmethod
    async def create_user(
        self,
        username: str,
        password: str,
        full_name: str = None,
        access_level: int = 0,
        organization: str = "Public",
    ) -> NoReturn:
        """
        Creates user with declared parameters
        * Should meet these criteria:
            1. organization number should be the same
            2. level of access of tokens user should be grater or equal than 2
            3. level of access of created user should be
               equal or less than level of tokens user

        Parameters
        ----------
        username: str
            username of user to delete
        password: str
            password of user
        full_name: str, optional
            name of user
            default: value of username
        organization: int, optional
            organization of user
            default: "Public"
        access_level: int, optional
            access_level of user
            default: 0
        """
        raise NotImplementedError

    @abstractmethod
    async def read_user(self, username: str) -> UserInfo:
        """
        Get information about user with given username

        Parameters
        ----------
        username: str
            username of user to delete

        Returns
        -------
        UserInfo (instance with those attributes)
            username: str
                username of user
            name: str
                name of user
            organization: str
                organization of user
            access_level: int
                access_level of user
        """
        raise NotImplementedError

    @abstractmethod
    async def update_user(
        self,
        username: str,
        new_username: Optional[str] = None,
        password: Optional[str] = None,
        name: Optional[str] = None,
        access_level: Optional[int] = None,
        organization: Optional[str] = None,
    ) -> NoReturn:
        """
        Updates user with given username

        Parameters
        ----------
        username: str
            username of user to delete
        new_username: str, optional
            new username to replace previous
        password: str, optional
            password of user
        name: str, optional
            name of user to update to
        organization: int, optional
            organization of user to update to
        access_level: int, optional
            access_level of user to update to
        """
        raise NotImplementedError

    @abstractmethod
    async def delete_user(self, username: str, test) -> NoReturn:
        """
        Removes user with given username

        Parameters
        ----------
        username: str
            username of user to delete
        """
        raise NotImplementedError

    @abstractmethod
    async def sign_in(self, username: str, password: str,) -> str:
        """
        checks username and password and returns new token

        Parameters
        ----------
        username: str
            username of user
        password: str
            password of user

        Returns
        -------
        str
            signed token
        """
        raise NotImplementedError

    @abstractmethod
    async def sign_out(self,) -> NoReturn:
        """
        removes token with which request was sent
        """
        raise NotImplementedError

    @abstractmethod
    async def sign_out_everywhere(self,) -> NoReturn:
        """
        removes all tokens of current user
        """
        raise NotImplementedError

    @abstractmethod
    async def sign_up(self, user: NewUser) -> NoReturn:
        """
        creates new user with given info if invite code exists

        Parameters
        ----------
        user: NewUser
            info about new user
        """
        raise NotImplementedError

    @abstractmethod
    async def remove_token(self, token: str) -> NoReturn:
        """
        removes token

        Parameters
        ----------
        token: str
            token to remove
        """
        raise NotImplementedError

    @abstractmethod
    async def remove_tokens(self, token: List[str]) -> NoReturn:
        """
        removes tokens

        Parameters
        ----------
        token: List[str]
            list of tokens to remove
        """
        raise NotImplementedError

    @abstractmethod
    async def get_tokens(self, username: str) -> List[str]:
        """
        returns list of tokens issued to user with given username

        Parameters
        ----------
        username: str
            username of user for which to sort tokens

        Returns
        -------
        List[str]
            list containing found tokens
        """

    def create_router(
        self, token: Callable[[Optional[int], Optional[int]], Callable[[str], NoReturn]]
    ) -> APIRouter:
        router = APIRouter()

        @router.get(
            "/users/me",
            tags=["user"],
            response_model=str,
            dependencies=[Depends(self.token(greater_or_equal=1))],
        )
        async def read_current_user(authorization=Header(...)):
            """
            return info about user, associated with user from token in request
            """
            return authorization

        @router.put("/users/me", tags=["user"])
        async def update_current_user(user: FullUser):
            """
            updates info of user, associated with user from token in request
            """
            return True

        @router.delete("/users/me", tags=["user"])
        async def delete_current_user(user: FullUser):
            """
            removes user, associated with user from token in request
            """
            return True

        @router.post("/users", tags=["user"])
        async def create_user(user: FullUser) -> NoReturn:
            """
            creates user with provided username, password, organization and access_level

            Note
            ----
            * only users with access level of 2 and more can use this function
            * users are created in the same organization as the requester
            """
            await self.create_user(
                user.username,
                user.password,
                user.full_name,
                user.access_level,
                user.organization,
            )
            return

        @router.get("/users/{username}", tags=["user"], response_model=UserInfo)
        async def read_user(username: str) -> UserInfo:
            """
            reads info about requested user
            """
            return await self.read_user(username)

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

        @router.post("/signin", tags=["auth"], response_model=str)
        async def signin(user: Credentials) -> str:
            """
            generates new token if provided username and password are correct
            """
            return await self.sign_in(user.username, user.password)

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

        @router.post("/signup", tags=["auth"], response_model=str)
        async def signup(user: NewUser):
            """
            creates new user with provided username, password, organization, access_level and invitation code
            """
            return True

        @router.delete("/token", tags=["token"])
        async def delete_token(token_identifier: str):
            """
            removes token by provided identifier: either token itself or token uuid
            """
            return token_identifier

        @router.delete("/tokens", tags=["token"])
        async def delete_tokens(token_identifiers: List[str]):
            """
            removes token by provided identifier: either token itself or token uuid
            """
            return token_identifiers

        @router.get("/tokens", tags=["token"], response_model=List[str])
        async def get_tokens() -> List[str]:
            """
            returns all tokens, associated with user from token in request
            """
            return ["tokens"]

        return router
