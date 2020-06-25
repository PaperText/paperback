from abc import ABCMeta, abstractmethod
from typing import List, Callable, ClassVar, NoReturn, Optional

from fastapi import Header, Depends, FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware

from .base import Base
from .models import (
    NewUser,
    FullUser,
    UserInfo,
    Credentials,
    TokenTester,
    OrganisationInfo,
    FullOrganisationInfo,
)
from ..exceptions import TokenException


class BaseAuth(Base, metaclass=ABCMeta):
    """
    base class for all auth modules of PaperText

    Attributes
    ----------
    TYPE: str
        type of module (the default is "AUTH" and shouldn't be changed)
    DEFAULTS: Dict[str, int]
        python dict of default values for configuration (the default is {})
    requires_dir: bool
        describes if directory for storage will be provide to __init__ call
            (default is False)
    """

    TYPE: ClassVar[str] = "AUTH"

    @staticmethod
    def add_CORS(api: FastAPI) -> NoReturn:  # noqa: N802
        """
        adds CORS policy to api

        Parameters
        ----------
        api: FastAPI
            instance of api
        """
        api.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    def token_tester(
        self,
        greater_or_equal: Optional[int] = None,
        one_of: Optional[List[int]] = None,
    ) -> Callable[[str], UserInfo]:
        """
        validates token with given parameters

        validates tokens fields and checks that
            * access_level >= greater_or_equal if greater_or_equal is non None
            * if access_level exists ib one_of if one_of is not None

        Parameters
        ----------
        greater_or_equal: int
            minimum loa, tokens loa should be `>=`
        one_of: List[str]
            list of loa, tokens load should be `loa in one_of`

        Returns
        -------
        Callable[[str], UserInfo]
            function which accept `Auth` header and returns UserInfo from token

        """
        if greater_or_equal is None and one_of is None:
            raise ValueError("either greater_or_equal or one_of should be set")

        def fn(authorization: str = Header(...)) -> UserInfo:
            user: UserInfo = self.token2user(authorization)
            if (
                user.access_level < greater_or_equal
                or user.access_level not in one_of
            ):
                raise TokenException(token=authorization)
            return user

        return fn

    @abstractmethod
    def token2user(self, token: str) -> UserInfo:
        """
        decodes and validates token, returning user from token in "Auth" header

        Parameters
        ----------
        token: str
            token to decode

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
        raise NotImplementedError

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
    async def get_users(self) -> List[UserInfo]:
        """
        Administrative function, get list of all users

        Returns
        -------
            List[UserInfo]: list of users without password
        """

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
    async def delete_user(self, username: str) -> NoReturn:
        """
        Removes user with given username

        Parameters
        ----------
        username: str
            username of user to delete
        """
        raise NotImplementedError

    @abstractmethod
    async def create_org(self, name: str, title: str):
        """
        creates organisation with given name and title

        Parameters
        ----------
        name: str
            unique name of organisation, sequence of english letters
                without spaces
        title: str
            title of organisation, can be anything

        Returns
        -------

        """
        raise NotImplementedError

    @abstractmethod
    async def update_org(self, org_name: str, org_title: str):
        """
        updates title of organisation with given name

        Parameters
        ----------
        org_name: str
            name of organisation
        org_title: str
            new title of organisation

        Returns
        -------

        """
        raise NotImplementedError

    @abstractmethod
    async def delete_org(self, org_name: str):
        """
        removes organisation with given name

        Parameters
        ----------
        org_name: str
            name of organisation
        org_title: str
            new title of organisation

        Returns
        -------

        """
        raise NotImplementedError

    @abstractmethod
    async def get_orgs(self) -> List[OrganisationInfo]:
        """
        returns list with all organisations

        Returns
        -------
        List[OrganisationInfo]
            list of organisations
        """
        raise NotImplementedError

    @abstractmethod
    async def get_org_with_users(self, org_name: str) -> FullOrganisationInfo:
        """
        returns info about organisations with given name including list of users

        Returns
        -------
        FullOrganisationInfo
            organisations info with users
        """
        raise NotImplementedError

    def create_router(self, token_tester: TokenTester,) -> APIRouter:
        """
        creates router

        Note
        ----
        If programmer of a module wishes to add functionality the preferred way
            is to implement method `add_routes`

        Parameters
        ----------
        token_tester: TokenTester,
            function to use as a token manager in dependencies

        Returns
        -------

        """
        router = APIRouter()

        # token and signin
        @router.post(
            "/signin", tags=["auth_module", "auth"], response_model=str
        )
        async def signin(user: Credentials) -> str:
            """
            generates new token if provided username and password are correct
            """
            return await self.sign_in(user.username, user.password)

        @router.get("/signout", tags=["auth_module", "auth"])
        async def signout():
            """
            removes token from request
            """
            return True

        @router.get("/signout_everywhere", tags=["auth_module", "auth"])
        async def signout_everywhere():
            """
            removes all tokens, associated with tokens user
            """
            return True

        @router.post(
            "/signup", tags=["auth_module", "auth"], response_model=str
        )
        async def signup(user: NewUser):
            """
            creates new user with provided
                username, password, organization,
                access_level and invitation code
            """
            return True

        @router.delete("/token", tags=["auth_module", "token"])
        async def delete_token(token_identifier: str):
            """
            removes token by provided identifier:
                either token itself or token uuid
            """
            return token_identifier

        @router.delete("/tokens", tags=["auth_module", "token"])
        async def delete_tokens(token_identifiers: List[str]):
            """
            removes token by provided identifier:
                either token itself or token uuid
            """
            return token_identifiers

        @router.get(
            "/tokens", tags=["auth_module", "token"], response_model=List[str]
        )
        async def get_tokens() -> List[str]:
            """
            returns all tokens, associated with user from token in request
            """
            return ["tokens"]

        # current user
        @router.get(
            "/users/me",
            tags=["auth_module", "user"],
            response_model=str,
            dependencies=[Depends(token_tester(greater_or_equal=0))],
        )
        async def read_current_user(authorization=Header(...)):
            """
            return info about user, associated with user from token in request
            """
            return authorization

        @router.put("/users/me", tags=["auth_module", "user"])
        async def update_current_user(user: FullUser):
            """
            updates info of user, associated with user from token in request
            """
            return True

        @router.delete("/users/me", tags=["auth_module", "user"])
        async def delete_current_user(user: FullUser):
            """
            removes user, associated with user from token in request
            """
            return True

        # all users
        @router.get(
            "/users",
            tags=["auth_module", "user"],
            response_model=List[UserInfo],
        )
        async def get_users(user: FullUser) -> List[UserInfo]:
            """
            creates user with provided
                username, password, organization and access_level

            Note
            ----
            * only users with access level of 2 and more can use this function
            * users are created in the same organization as the requester
            """
            return await self.get_users()

        @router.post("/user", tags=["auth_module", "user"])
        async def create_user(user: FullUser) -> NoReturn:
            """
            creates user with provided
                username, password, organization and access_level

            Note
            ----
            * only users with access level of 2 and more can use this function
            * users are created in the same organization as the requester
            """
            return await self.create_user(
                user.username,
                user.password,
                user.full_name,
                user.access_level,
                user.organization,
            )

        @router.get(
            "/user/{username}",
            tags=["auth_module", "user"],
            response_model=UserInfo,
            dependencies=[Depends(token_tester(greater_or_equal=0))],
        )
        async def read_user(username: str) -> UserInfo:
            """
            reads info about requested user
            """
            return await self.read_user(username)

        @router.put("/user/{username}", tags=["auth_module", "user"])
        async def update_users(username: str):
            """
            updates info about requested user
            """
            return username

        @router.delete("/user/{username}", tags=["auth_module", "user"])
        async def remove_users(username: str):
            """
            removes requested user
            """
            return username

        # Organisations
        @router.get(
            "/orgs",
            tags=["auth_module", "organisations"],
            response_model=List[OrganisationInfo],
        )
        async def get_organisations() -> List[OrganisationInfo]:
            """
            returns list of organisations
            """
            return await self.get_orgs()

        @router.post("/org", tags=["auth_module", "organisations"])
        async def create_organisation(org_info: OrganisationInfo):
            """
            creates organisation with given parameters
            """
            return await self.create_org(org_info.name, org_info.title)

        @router.put("/org/{org_name}", tags=["auth_module", "organisations"])
        async def update_organisation(org_name: str, org_title: str):
            """
            updates title of organisation with given name to given
                organisation title
            """
            return await self.update_org(org_name, org_title)

        @router.delete(
            "/org/{org_name}", tags=["auth_module", "organisations"]
        )
        async def delete_organisation(org_name: str):
            """
            removes organisation with given name
            """
            return await self.delete_org(org_name)

        @router.get(
            "/org/{org_name}",
            tags=["auth_module", "organisations"],
            response_model=FullOrganisationInfo,
        )
        async def get_info(org_name: str) -> FullOrganisationInfo:
            """
            return information about organisation with list of users in it
            """
            return await self.get_org_with_users(org_name)

        self.add_routes(router)
        return router
