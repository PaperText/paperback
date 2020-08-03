from abc import ABCMeta, abstractmethod
from typing import Dict, List, Union, Callable, ClassVar, NoReturn, Optional

from fastapi import (
    Body,
    Header,
    Depends,
    FastAPI,
    APIRouter,
    HTTPException,
    status,
)
from pydantic import EmailStr
from fastapi.middleware.cors import CORSMiddleware

from .base import Base
from .models import (
    NewUser,
    TokenRes,
    UserInfo,
    InviteCode,
    OrgListRes,
    Credentials,
    TokenTester,
    Organisation,
    TokenListRes,
    OrgUpdateName,
    NewInvitedUser,
    OrgUpdateOrgId,
    UserListResponse,
    InviteCodeListRes,
    MinimalInviteCode,
    UserUpdateFullName,
    UserUpdatePassword,
    UserUpdateUsername,
    MinimalOrganisation,
)


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

    public_org_id: str = "org:public"

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
            minimum loa, i.e. tokens loa should be `>=` than greater_or_equal
        one_of: List[str]
            list of ints, tokens loa should be `loa in one_of`

        Returns
        -------
        Callable[[str], UserInfo]
            function which accept `Authentication` header
            and returns UserInfo from token

        """
        if greater_or_equal is None and one_of is None:
            raise ValueError("either greater_or_equal or one_of should be set")

        def fn(authentication: str = Header(...)) -> UserInfo:
            token: str = (
                authentication[7:]
                # authentication.removeprefix("Bearer: ")
                if authentication.startswith("Bearer: ")
                else authentication
            )
            print(authentication, token)
            user: UserInfo = UserInfo(**self.token2user(authentication))
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
    def token2user(self, token: str) -> Dict[str, Union[str, int]]:
        """
        decodes and validates token, returning user from token in "Authentication" header

        Parameters
        ----------
        token: str
            token to decode

        Returns
        -------
        Dict[str, Union[str, int]]
            username: str
                username of user
            email: str
                email of user
            organization: str
                organization of user
            level_of_access: int
                access_level of user
            fullname: str, optional
                name of user
        """
        raise NotImplementedError

    @abstractmethod
    async def signin(
        self,
        password: str,
        email: Optional[str] = None,
        username: Optional[str] = None,
    ) -> str:
        """
        checks username and password and returns new token

        Parameters
        ----------
        password: str
            password of user
        email: str, optional
            email of user
        username: str, optional
            username of user

        Notes
        -----
        either email or username must be provided

        Returns
        -------
        str
            JSON Web Token
        """
        raise NotImplementedError

    @abstractmethod
    async def signup(
        self,
        username: str,
        email: EmailStr,
        password: str,
        invitation_code: str,
        fullname: Optional[str] = None,
    ) -> str:
        """
        creates new user with given info if invite code exists

        Parameters
        ----------
        username: str
            new username of user, must be unique
        email: str
            email of new user, must be unique
        password: str
            password of new user
        invitation_code: str
            invitation code
        fullname: str, optional
            fullname of user

        Returns
        -------
        str
            token of created user
        """
        raise NotImplementedError

    # @abstractmethod
    # async def signout(self, token: str) -> NoReturn:
    #     """
    #     removes token with which request was sent
    #
    #     Parameters
    #     ----------
    #     token: str
    #         token to remove
    #     """
    #     raise NotImplementedError

    @abstractmethod
    async def signout_everywhere(self, username: str) -> NoReturn:
        """
        removes all tokens of current user

        Parameters
        ----------
        username: str
            username, whose tokens will be removed
        """
        raise NotImplementedError

    @abstractmethod
    async def get_tokens(self, username: str) -> List[str]:
        """
        returns list of tokens issued to user with given username

        Parameters
        ----------
        username: str
            username of user for which to return tokens

        Returns
        -------
        List[str]
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
    async def create_user(
        self,
        username: str,
        email: EmailStr,
        password: str,
        level_of_access: int = 0,
        organisation: Optional[str] = None,
        fullname: Optional[str] = None,
    ) -> Dict[str, Union[str, int]]:
        """
        Creates user from provided info

        Parameters
        ----------
        username: str
            new users username
        email: str
            new users email
        password: str
            new users password
        level_of_access: int, default is 0
            loa of new user
        organisation: str, optional
            organisation of user.
            If none is provided then user will be in public org
        fullname: str, optional
            fullname of new user

        Returns
        -------
        Dict[str, Union[str, int]]
            username: str
                username of user
            email: str
                email of user
            organization: str
                organization of user
            level_of_access: int
                access_level of user
            fullname: str, optional
                name of user
        """
        raise NotImplementedError

    @abstractmethod
    async def read_user(self, username: str) -> Dict[str, Union[str, int]]:
        """
        Get information about user with given username

        Parameters
        ----------
        username: str
            username of user to delete

        Returns
        -------
        Dict[str, Union[str, int]]
            username: str
                username of user
            email: str
                email of user
            organization: str
                organization of user
            level_of_access: int
                access_level of user
            fullname: str, optional
                name of user
        """
        raise NotImplementedError

    @abstractmethod
    async def read_users(self) -> List[Dict[str, Union[str, int]]]:
        """
        reads all users and returns info in list of dicts

        Returns
        -------
        List[Dict[str, Union[str, int]]]:
            list of users without password
            Dict[str, Union[str, int]]
                username: str
                    username of user
                email: str
                    email of user
                organization: str
                    organization of user
                level_of_access: int
                    access_level of user
                fullname: str, optional
                    name of user
        """

    @abstractmethod
    async def update_user(
        self,
        username: str,
        new_username: Optional[str] = None,
        new_fullname: Optional[str] = None,
        new_level_of_access: Optional[int] = None,
        new_organisation: Optional[str] = None,
    ) -> Dict[str, Union[str, int]]:
        """
        Updates user with given username

        Parameters
        ----------
        username: str
            username of user to delete
        new_username: str, optional
            default: None
            new username to replace previous
        new_fullname: str, optional
            default: None
            new fullname to replace previous
        new_level_of_access: int, optional
            default: None
            new level_of_access to replace previous
        new_organisation: str, optional
            default: None
            new organization to replace previous

        Returns
        -------
        Dict[str, Union[str, int]]
        user object with new info
            username: str
                username of user
            email: str
                email of user
            organization: str
                organization of user
            level_of_access: int
                access_level of user
            fullname: str, optional
                name of user
        """
        raise NotImplementedError

    @abstractmethod
    async def update_user_password(
        self,
        username: str,
        old_passwords: Optional[str] = None,
        new_password: Optional[str] = None,
    ) -> Dict[str, Union[str, int]]:
        """
        Updates user with given username

        Parameters
        ----------
        username: str
            username of user to delete
        old_passwords: str, optional
            default: None
            old password to check
        new_password: str, optional
            default: None
            new password to replace previous

        Returns
        -------
        Dict[str, Union[str, int]]
        user object with new info
            username: str
                username of user
            email: str
                email of user
            organization: str
                organization of user
            level_of_access: int
                access_level of user
            fullname: str, optional
                name of user
        """
        raise NotImplementedError

    @abstractmethod
    async def update_user_email(
        self, username: str, new_email: str
    ) -> Dict[str, Union[str, int]]:
        """
        Updates user with given username

        Parameters
        ----------
        username: str
            username of user to delete
        new_email: str
            new email to replace previous

        Returns
        -------
        Dict[str, Union[str, int]]
        user object with new info
            username: str
                username of user
            email: str
                email of user
            organization: str
                organization of user
            level_of_access: int
                access_level of user
            fullname: str, optional
                name of user
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
    async def create_invite_code(
        self, issuer: str, organisation_id: str
    ) -> str:
        """
        creates invite code

        Parameters
        ----------
        issuer: str
            issuer of invite code
        organisation_id: str
            id of organisation to add user to

        Returns
        -------
        str
            new invite code
        """
        raise NotImplementedError

    @abstractmethod
    async def read_invite_code(self, code: str) -> Dict[str, str]:
        """
        returns info about invite code

        Returns
        ----------
        Dict[str, str]
            code: str
            issuer_id: str
            num_registered: int
        """
        raise NotImplementedError

    @abstractmethod
    async def read_invite_codes(self) -> List[Dict[str, str]]:
        """
        returns created invite codes

        Returns
        ----------
        List[Dict[str, str]]
            list of invite codes
            Dict[str, str]
                code: str
                issuer_id: str
                num_registered: int
        """
        raise NotImplementedError

    @abstractmethod
    async def delete_invite_codes(self, code: str):
        """
        removes invite code

        Parameters
        ----------
        code: str
            invite code to remove
        """
        raise NotImplementedError

    @abstractmethod
    async def create_org(
        self, organisation_id: str, name: Optional[str] = None,
    ) -> Dict[str, Union[str, List[str]]]:
        """
        creates organisation with given name and title

        Parameters
        ----------
        organisation_id: str
            id of new organisation
        name: str, optional
            name of new organisation

        Returns
        -------
        Dict[str, Union[str, List[str]]]
            new organisation
            organisation_id: str,
            users: List[str]
            name: str, optional
        """
        raise NotImplementedError

    @abstractmethod
    async def read_org(
        self, organisation_id: str
    ) -> Dict[str, Union[str, List[str]]]:
        """
        returns info about organisation with given `organisation_id`

        Parameters
        ----------
        organisation_id: str
            id of organisation to return

        Returns
        -------
        Dict[str, Union[str, List[str]]]
            new organisation
            organisation_id: str,
            users: List[str]
            name: str, optional
        """
        raise NotImplementedError

    @abstractmethod
    async def read_orgs(
        self, columns: Optional[List[str]] = None
    ) -> List[Dict[str, str]]:
        """
        returns list with all organisations

        Parameters
        ----------
        columns: List[str], optional
            list of columns. If `None` then all columns are selected

        Returns
        -------
        List[Dict[str, str]]
            list of organisations
            Dict[str, str]
            mapping from column to value, depends on `columns`
                organisation_id: str
                    id of organisation
                name: str, optional
                    name of organisation
        """
        raise NotImplementedError

    @abstractmethod
    async def update_org(
        self,
        old_organisation_id: str,
        new_organisation_id: Optional[str] = None,
        new_name: Optional[str] = None,
    ) -> Dict[str, str]:
        """
        updates title of organisation with given name

        Parameters
        ----------
        old_organisation_id: str
            id of organisation
        new_organisation_id: str, optional
            new id of organisation
        new_name: str
            new name of organisation

        Returns
        -------
        Dict[str, str]
        new organisation
            organisation_id: str
                id of organisation
            name: str, optional
                name of organisation
        """
        raise NotImplementedError

    @abstractmethod
    async def delete_org(self, organisation_id: str):
        """
        removes organisation with given name

        Parameters
        ----------
        organisation_id: str
            id of organisation
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
        async def signin(credentials: Credentials) -> TokenRes:
            """
            generates new token if provided username and password are correct
            """
            return TokenRes(response=await self.signin(**dict(credentials)))

        @router.post(
            "/signup", tags=["auth_module", "auth"], response_model=TokenRes,
        )
        async def signup(user: NewInvitedUser) -> TokenRes:
            """
            creates new user with provided
                username, password, name and invitation code
            """
            return TokenRes(response=await self.signup(**dict(user)))

        @router.get("/signout", tags=["auth_module", "auth"])
        async def signout(
            # requester: UserInfo = Depends(token_tester(greater_or_equal=0)),
            authentication: str = Header(...),
        ):
            """
            removes token from db of tokens
            """
            token: str = (
                authentication[7:]
                # authentication.removeprefix("Bearer: ")
                if authentication.startswith("Bearer: ")
                else authentication
            )
            await self.remove_token(token)

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
            tokens = await self.get_tokens(requester.username)
            return TokenListRes(response=tokens)

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
            await self.remove_tokens(token_identifiers)

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
            return UserInfo(
                **(await self.create_user(**dict(user))),
                level_of_access=0,
                organisation="org:public",
            )

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
            return UserInfo(**(await self.read_user(username)))

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
            raw_users: List[
                Dict[str, Union[str, int]]
            ] = await self.read_users()
            users: List[UserInfo] = [UserInfo(**user) for user in raw_users]
            return UserListResponse(response=users)

        @router.put(
            "/usr/{username}:username",
            tags=["auth_module", "user", "access_level_2"],
        )
        async def update_users_username(
            username: str,
            new_username: UserUpdateUsername,
            requester: UserInfo = Depends(token_tester(greater_or_equal=2)),
        ):
            """
            changes username of user with given username
            """
            user: UserInfo = UserInfo(**(await self.read_user(username)))
            if requester.level_of_access == 3:
                pass
            elif user.level_of_access >= requester.level_of_access:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Can't edit user with higher or same privileges",
                )
            return await self.update_user(
                username=username, new_username=new_username.new_username
            )

        @router.put(
            "/usr/{username}:password",
            tags=["auth_module", "user", "access_level_2"],
        )
        async def update_users_password(
            username: str,
            passwords: UserUpdatePassword,
            requester: UserInfo = Depends(token_tester(greater_or_equal=2)),
        ):
            """
            changes password of user with given username
            """
            user: UserInfo = UserInfo(**(await self.read_user(username)))
            if requester.level_of_access == 3:
                pass
            elif user.level_of_access >= requester.level_of_access:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Can't edit user with higher or same privileges",
                )
            await self.update_user_password(
                username=username,
                old_passwords=passwords.old_password,
                new_password=passwords.new_password,
            )

        @router.put(
            "/usr/{username}:fullname",
            tags=["auth_module", "user", "access_level_2"],
        )
        async def update_users_fullname(
            username: str,
            new_fullname: UserUpdateFullName,
            requester: UserInfo = Depends(token_tester(greater_or_equal=2)),
        ):
            """
            changes fullname of user with given username
            """
            user: UserInfo = UserInfo(**(await self.read_user(username)))
            if requester.level_of_access == 3:
                pass
            elif user.level_of_access >= requester.level_of_access:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Can't edit user with higher or same privileges",
                )
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
            user: UserInfo = UserInfo(**(await self.read_user(username)))
            if requester.level_of_access == 3:
                pass
            elif user.level_of_access >= requester.level_of_access:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Can't edit user with higher or same privileges",
                )
            new_loa: int = min(
                user.level_of_access + 1, requester.level_of_access
            )
            return await self.update_user(
                username=username, new_level_of_access=new_loa
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
            user: UserInfo = UserInfo(**(await self.read_user(username)))
            if requester.level_of_access == 3:
                pass
            elif user.level_of_access >= requester.level_of_access:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Can't edit user with higher or same privileges",
                )
            new_loa: int = max(
                user.level_of_access - 1, requester.level_of_access
            )
            return await self.update_user(
                username=username, new_level_of_access=new_loa
            )

        @router.delete(
            "/usr/{username}", tags=["auth_module", "user", "access_level_2"]
        )
        async def delete_user(
            username: str,
            requester: UserInfo = Depends(token_tester(greater_or_equal=1)),
        ):
            """
            removes user, associated with user from token in request
            """
            user: UserInfo = UserInfo(**(await self.read_user(username)))
            if requester.level_of_access == 3:
                pass
            elif user.level_of_access >= requester.level_of_access:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Can't edit user with higher or same privileges",
                )
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
            raw_orgs: List[Dict[str, str]] = await self.read_orgs()
            orgs: List[MinimalOrganisation] = [
                MinimalOrganisation(**org) for org in raw_orgs
            ]
            return OrgListRes(response=orgs)

        @router.post(
            "/org",
            tags=["auth_module", "organisation", "access_level_3"],
            dependencies=[Depends(token_tester(greater_or_equal=3))],
        )
        async def create_organisation(org: MinimalOrganisation):
            """
            creates new organisation with given org_id and name
            """
            await self.create_org(org.organisation_id, org.name)

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
            return Organisation(**(await self.read_org(org_id)))

        @router.put(
            "/org/{org_id}:org_id",
            tags=["auth_module", "organisation", "access_level_2"],
            dependencies=[Depends(token_tester(greater_or_equal=2))],
        )
        async def update_org_organisation_id(
            org_id: str, new_org_id: OrgUpdateOrgId,
        ):
            """
            changes org_id of organisation to new_org_id
            """
            await self.update_org(
                org_id, new_organisation_id=new_org_id.new_organisation_id
            )

        @router.put(
            "/org/{org_id}:name",
            tags=["auth_module", "organisation", "access_level_2"],
            dependencies=[Depends(token_tester(greater_or_equal=2))],
        )
        async def update_org_name(
            org_id: str, new_name: OrgUpdateName,
        ):
            """
            changes name of organisation with given org_id to new_name
            """
            await self.update_org(org_id, new_name=new_name.new_name)

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
                **dict(user), level_of_access=1, organisation=org_id
            )

        @router.put(
            "/org/{org_id}/usr/{username}",
            tags=["auth_module", "organisation", "access_level_3"],
        )
        async def add_user_to_org(
            org_id: str,
            username: str,
            requester: UserInfo = Depends(token_tester(greater_or_equal=3)),
        ):
            """
            adds user with provided username to organisation with given org_id
            if he is in public organisation
            """
            user: UserInfo = UserInfo(**(await self.read_user(username)))
            if requester.level_of_access == 3:
                pass
            elif user.level_of_access >= requester.level_of_access:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Can't edit user with higher or same privileges",
                )
            if user.organisation == "org:public":
                await self.update_user(username, new_organisation=org_id)
            else:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="can't invite user from non-public organisations",
                )

        @router.delete(
            "/org/{org_id}/usr/{username}",
            tags=["auth_module", "organisation"],
        )
        async def delete_user_from_org(
            org_id: str,
            username: str,
            requester: UserInfo = Depends(token_tester(greater_or_equal=3)),
        ):
            """
            removes requested user
            """
            user: UserInfo = UserInfo(**(await self.read_user(username)))
            if requester.level_of_access == 3:
                pass
            elif user.level_of_access >= requester.level_of_access:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Can't edit user with higher or same privileges",
                )
            if user.organisation != "org:public":
                await self.update_user(username, new_organisation=org_id)
            else:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="can't remove user from public organisations",
                )

        @router.delete(
            "/org/{org_id}",
            tags=["auth_module", "organisation", "access_level_3"],
            dependencies=[Depends(token_tester(greater_or_equal=3))],
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
        ) -> str:
            """
            creates invite code
            accepts list of docs and corpuses to provide to guest
            """
            if requester.level_of_access == 3:
                pass
            else:
                if invite_code.organisation_id not in [
                    self.public_org_id,
                    requester.organisation,
                ]:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="can't invite to non-user or non-public organisation",
                    )
            return await self.create_invite_code(
                requester.username, invite_code.organisation_id
            )

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
            raw_codes: List[Dict[str, str]] = await self.read_invite_codes()
            codes: List[InviteCode] = [
                InviteCode(**code) for code in raw_codes
            ]
            if requester.level_of_access == 3:
                return InviteCodeListRes(response=codes)
            if requester.level_of_access == 2:
                new_codes: List[InviteCode] = []
                for code in codes:
                    user: UserInfo = UserInfo(
                        **(await self.read_user(code.issuer_id))
                    )
                    if (
                        user.organisation == requester.organisation
                        or user.username == requester.username
                        or code.organisation_id == self.public_org_id
                    ):
                        new_codes.append(code)
                return InviteCodeListRes(response=new_codes)
            else:
                new_codes: List[InviteCode] = []
                for code in codes:
                    user: UserInfo = UserInfo(
                        **(await self.read_user(code.issuer_id))
                    )
                    if (
                        user.username == requester.username
                        or code.organisation_id == self.public_org_id
                    ):
                        new_codes.append(code)
                return InviteCodeListRes(response=new_codes)

        @router.get(
            "/invite/{invite_code}",
            tags=["auth_module", "invite", "access_level_1"],
            response_model=InviteCode,
        )
        async def read_invite_code(invite_code: str,) -> InviteCode:
            """
            acquires info about invite code with given code
            """
            return InviteCode(**(await self.read_invite_code(invite_code)))

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
            codes: List[InviteCode] = (
                await read_invite_codes(requester=requester)
            ).response
            codes_str: List[str] = [code.code for code in codes]
            if invite_code not in codes_str:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="can't delete this invite code",
                )

            await self.delete_invite_codes(invite_code)

        self.add_routes(router)
        return router
