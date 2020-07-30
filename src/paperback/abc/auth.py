from abc import ABCMeta, abstractmethod
from typing import List, Callable, ClassVar, NoReturn, Optional

from fastapi import (
    Body,
    Header,
    Depends,
    FastAPI,
    APIRouter,
    HTTPException,
    status,
)
from fastapi.middleware.cors import CORSMiddleware

from .base import Base
from .models import *


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

        def fn(Authentication: str = Header(...)) -> UserInfo:
            user: UserInfo = self.token2user(Authentication)
            if (
                user.level_of_access < greater_or_equal
                or user.level_of_access not in one_of
            ):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Could not validate credentials",
                )
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
    async def signin(self, credentials: Credentials) -> str:
        """
        checks username and password and returns new token

        Parameters
        ----------
        credentials: Credentials
            username and password of new user

        Returns
        -------
        str
            signed token
        """
        raise NotImplementedError

    @abstractmethod
    async def signup(self, user: NewInvitedUser) -> str:
        """
        creates new user with given info if invite code exists

        Parameters
        ----------
        user: NewInvitedUser
            info about new user
        """
        raise NotImplementedError

    @abstractmethod
    async def signout(self, user: UserInfo) -> NoReturn:
        """
        removes token with which request was sent

        Parameters
        ----------
        user: UserInfo
            info about user to sign out
        """
        raise NotImplementedError

    @abstractmethod
    async def signout_everywhere(self,) -> NoReturn:
        """
        removes all tokens of current user
        """
        raise NotImplementedError

    @abstractmethod
    async def get_tokens(self, user: UserInfo) -> List[str]:
        """
        returns list of tokens issued to user with given username

        Parameters
        ----------
        username: str
            username of user for which to sort tokens

        Returns
        -------
        TokenListRes
            list containing found tokens
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
    async def create_user(self, user: NewUser,) -> UserInfo:
        """
        Creates user from provided info

        Parameters
        ----------
        user: NewUser
            new user description
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
    async def read_users(self) -> List[UserInfo]:
        """
        Administrative function, get list of all users

        Returns
        -------
            List[UserInfo]: list of users without password
        """

    @abstractmethod
    async def update_user(
        self,
        username: str,
        new_username: Optional[str] = None,
        passwords: Optional[UserUpdatePassword] = None,
        new_fullname: Optional[str] = None,
        new_level_of_access: Optional[int] = None,
        new_organization: Optional[str] = None,
    ) -> UserInfo:
        """
        Updates user with given username

        Parameters
        ----------
        username: str
            username of user to delete
        new_username: str, optional
            default: None
            new username to replace previous
        passwords: UserUpdatePassword, optional
            default: None
            password to replace previous, including old password
        new_fullname: str, optional
            default: None
            new fullname to replace previous
        new_level_of_access: int, optional
            default: None
            new level_of_access to replace previous
        new_organization: str, optional
            default: None
            new organization to replace previous

        Returns
        -------
        UserInfo
            user object with new info
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
    async def create_invite_code(self, gives_access: List[str]):
        """
        creates invite code

        Parameters
        ----------
        gives_access: List[str]
            list of docs and corpuses to provide to guest
        """
        raise NotImplementedError

    @abstractmethod
    async def read_invite_codes(self) -> List[InviteCode]:
        """
        returns created invite codes

        Returns
        ----------
        List[InviteCode]
            list of invite codes
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
    async def get_orgs(self) -> List[MinimalOrganisation]:
        """
        returns list with all organisations

        Returns
        -------
        List[MinimalOrganisation]
            list of organisations
        """
        raise NotImplementedError

    @abstractmethod
    async def get_org_with_users(self, org_name: str) -> Organisation:
        """
        returns info about organisations with given name including list of users

        Returns
        -------
        Organisation
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
        fastapi.APIRouter,
            router with all paths
        """
        router = APIRouter()

        # signin and signout
        @router.post(
            "/signin", tags=["auth_module", "auth"], response_model=TokenRes
        )
        async def signin(сredentials: Credentials) -> TokenRes:
            """
            generates new token if provided username and password are correct
            """
            return TokenRes(response=await self.sign_in(сredentials))

        @router.post(
            "/signup", tags=["auth_module", "auth"], response_model=TokenRes,
        )
        async def signup(user: NewInvitedUser) -> TokenRes:
            """
            creates new user with provided
                username, password, name and invitation code
            """
            return TokenRes(response=await self.sign_up(user))

        @router.get("/signout", tags=["auth_module", "auth"])
        async def signout(
            requester: UserInfo = Depends(token_tester(greater_or_equal=0)),
        ) -> NoReturn:
            """
            removes token from db of tokens
            """
            await self.sign_out(UserInfo)

        @router.get("/signout_everywhere", tags=["auth_module", "auth"])
        async def signout_everywhere() -> NoReturn:
            """
            removes all tokens, associated with tokens user
            """

        # tokens
        @router.get(
            "/tokens",
            tags=["auth_module", "token"],
            response_model=TokenListRes,
        )
        async def get_tokens(
            requester: UserInfo = Depends(token_tester(greater_or_equal=0)),
        ) -> TokenListRes:
            """
            returns all tokens, associated with user from token in request
            """
            return TokenListRes(response=await self.get_tokens(requester))

        @router.delete("/token", tags=["auth_module", "token"])
        async def delete_token(token_identifier: str = Body(...)):
            """
            removes token by provided identifier:
                either token itself or token uuid
            """
            await self.remove_token(token_identifier)

        @router.delete("/tokens", tags=["auth_module", "token"])
        async def delete_tokens(token_identifiers: List[str]):
            """
            removes token by provided identifiers:
                either token itself or token uuid
            """
            await self.remove_token(token_identifiers)

        # +-------+
        # | users |
        # +-------+
        @router.post(
            "/usr",
            tags=["auth_module", "user", "access_level_2"],
            response_model=UserInfo,
        )
        async def create_user(user: NewUser) -> UserInfo:
            """
            creates user with provided username, password and fullname

            Note
            ----
            * created users are assigned to public organisation
            * created users loa is 1
            """
            return await self.create_user(user)

        @router.get(
            "/me",
            tags=["auth_module", "user", "access_level_0"],
            response_model=UserInfo,
        )
        async def get_me(
            requester: UserInfo = Depends(token_tester(greater_or_equal=0)),
        ) -> UserInfo:
            """
            returns all tokens, associated with user from token in request
            """
            return requester

        @router.get(
            "/usr/{username}",
            tags=["auth_module", "user", "access_level_2"],
            response_model=UserInfo,
        )
        async def read_user(username: str) -> UserInfo:
            """
            return info about user with given username
            """
            return await self.read_user(username)

        @router.get(
            "/usrs",
            tags=["auth_module", "user", "access_level_3"],
            response_model=UserListResponse,
        )
        async def read_all_users() -> UserListResponse:
            """
            reads all existing users

            created users are assigned to public organisation
            """
            return UserListResponse(response=await self.read_users())

        @router.put(
            "/usr/{username}:username",
            tags=["auth_module", "user", "access_level_2"],
        )
        async def update_users_username(
            username: str, new_username: UserUpdateUsername
        ):
            """
            changes username of user with given username
            """
            return await self.update_user(
                username=username, new_username=new_username.new_username
            )

        @router.put(
            "/usr/{username}:password",
            tags=["auth_module", "user", "access_level_2"],
        )
        async def update_users_password(
            username: str, passwords: UserUpdatePassword
        ):
            """
            changes password of user with given username
            """
            return await self.update_user(
                username=username, passwords=passwords
            )

        @router.put(
            "/usr/{username}:fullname",
            tags=["auth_module", "user", "access_level_2"],
        )
        async def update_users_fullname(
            username: str, new_fullname: UserUpdateFullName
        ):
            """
            changes fullname of user with given username
            """
            return await self.update_user(
                username=username, new_fullname=new_fullname.new_fullname
            )

        @router.get(
            "/usr/{username}:promote",
            tags=["auth_module", "user", "access_level_2"],
        )
        async def promote_user(
            username: str,
            requester: UserInfo = Depends(token_tester(greater_or_equal=1)),
        ):
            """
            increases loa of user with given username

            Note
            ----
            Maximum loa is equal to requesters loa
            """
            user: UserInfo = await self.read_user(username)
            new_loa: int = min(
                user.level_of_access + 1, requester.level_of_access
            )
            return await self.update_user(
                username=username, new_level_of_access=user
            )

        @router.get(
            "/usr/{username}:demote",
            tags=["auth_module", "user", "access_level_2"],
        )
        async def demote_user(
            username: str,
            requester: UserInfo = Depends(token_tester(greater_or_equal=1)),
        ):
            """
            decreases loa of user with given username

            Note
            ----
            Minimum loa is 0
            """
            user: UserInfo = await self.read_user(username)
            new_loa: int = min(
                user.level_of_access + 1, requester.level_of_access
            )
            return await self.update_user(
                username=username, new_level_of_access=user
            )

        @router.delete(
            "/usr/{username}", tags=["auth_module", "user", "access_level_2"]
        )
        async def delete_user(username: str):
            """
            removes user, associated with user from token in request
            """
            await self.delete_user(username)

        # +--------------+
        # | organisation |
        # +--------------+
        @router.get(
            "/orgs",
            tags=["auth_module", "organisation", "access_level_3"],
            response_model=OrgListRes,
            dependencies=[Depends(token_tester(greater_or_equal=3))],
        )
        async def read_organisations() -> OrgListRes:
            """
            returns list of organisations
            """
            return await self.get_orgs()

        @router.post(
            "/org",
            tags=["auth_module", "organisation", "access_level_3"],
            dependencies=[Depends(token_tester(greater_or_equal=3))],
        )
        async def create_organisation(org: MinimalOrganisation):
            """
            creates new organisation with given org_id and name
            """
            await self.create_org(org.org_id, org.name)

        @router.get(
            "/org/{org_id}",
            tags=["auth_module", "organisation", "access_level_3"],
            response_model=Organisation,
            dependencies=[Depends(token_tester(greater_or_equal=3))],
        )
        async def read_organisation(org_id: str) -> Organisation:
            """
            returns info about organisation with given `org_id`
            """
            return await self.get_org(org_id)

        @router.put(
            "/org/{org_id}:org_id",
            tags=["auth_module", "organisation", "access_level_2"],
            dependencies=[Depends(token_tester(greater_or_equal=2))],
        )
        async def update_orgid_of_org(
            org_id: str, new_org_id: OrgUpdateOrgId,
        ):
            """
            changes org_id of organisation to new_org_id
            """
            await self.update_org(org_id, org_id=new_org_id)

        @router.put(
            "/org/{org_id}:name",
            tags=["auth_module", "organisation", "access_level_2"],
            dependencies=[Depends(token_tester(greater_or_equal=2))],
        )
        async def update_name_of_org(
            org_id: str, new_name: OrgUpdateName,
        ):
            """
            changes name of organisation with given org_id to new_name
            """
            await self.update_org(org_id, name=new_name)

        @router.post(
            "/org/{org_id}/usr",
            tags=["auth_module", "organisation", "access_level_3"],
            dependencies=[Depends(token_tester(greater_or_equal=3))],
        )
        async def create_user_in_org(
            org_id: str, user: NewUser,
        ):
            """
            creates user with provided username, password and fullname
            in organisation with given id

            Note
            ----
            * created users are assigned to requesters organisation
            * created users loa is 1
            """
            return await self.create_user(
                user.username, user.password, user.fullname, 1, org_id
            )

        @router.put(
            "/org/{org_id}/usr/{username}",
            tags=["auth_module", "organisation", "access_level_3"],
            dependencies=[Depends(token_tester(greater_or_equal=3))],
        )
        async def add_user_to_org(org_id: str, username: str):
            """
            adds user with provided username to organisation with given org_id
            if he is in public organisation
            """

        @router.delete(
            "/org/{org_id}/usr/{username}",
            tags=["auth_module", "organisation"],
        )
        async def delete_user_from_org(org_id: str, username: str):
            """
            removes requested user
            """
            return username

        @router.delete(
            "/org/{org_id}",
            tags=["auth_module", "organisation", "access_level_2"],
            dependencies=[Depends(token_tester(greater_or_equal=2))],
        )
        async def delete_organisation(org_id: str):
            """
            removes organisation with given name
            """
            return await self.delete_org(org_id)

        # +---------+
        # | Invites |
        # +---------+

        @router.post(
            "/invite", tags=["auth_module", "invite", "access_level_1"],
        )
        async def create_invite_code(
            invite_code: MinimalInviteCode,
            requester: UserInfo = Depends(token_tester(greater_or_equal=1)),
        ):
            """
            creates invite code
            accepts list of docs and corpuses to provide to guest
            """
            return await self.create_invite_code(invite_code)

        @router.get(
            "/invites",
            tags=["auth_module", "invite", "access_level_1"],
            response_model=InviteCodeListRes,
        )
        async def read_invite_codes(
            requester: UserInfo = Depends(token_tester(greater_or_equal=1)),
        ) -> InviteCodeListRes:
            """
            acquires invite codes
            """
            return await self.read_invite_codes()

        @router.get(
            "/invite/{invite_code}",
            tags=["auth_module", "invite", "access_level_1"],
            response_model=InviteCode,
        )
        async def read_invite_code(
            invite_code: str,
            requester: UserInfo = Depends(token_tester(greater_or_equal=1)),
        ) -> InviteCode:
            """
            acquires info about invite code with given code
            """
            return await self.read_invite_code(invite_code)

        # @router.put(
        #     "/invite/{invite_code}",
        #     tags=["auth_module", "invite", "access_level_1"],
        #     response_model=List[InviteCode],
        # )
        # async def update_invite_code(
        #     invite_code: str,
        #     requester: UserInfo = Depends(token_tester(greater_or_equal=1)),
        # ) -> List[InviteCode]:
        #     """
        #     acquires invite codes
        #     """
        #     return await self.read_invite_codes()

        @router.delete(
            "/invite/{invite_code}",
            tags=["auth_module", "invite", "access_level_1"],
        )
        async def delete_invite_code(
            invite_code: str,
            requester: UserInfo = Depends(token_tester(greater_or_equal=1)),
        ):
            """
            delete invite code by code itself
            """
            return await self.read_invite_codes()

        self.add_routes(router)
        return router
