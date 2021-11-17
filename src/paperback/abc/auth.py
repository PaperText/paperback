from abc import ABCMeta, abstractmethod
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Callable, ClassVar, Dict, Final, List, Optional, Union

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Body,
    Depends,
    FastAPI,
    Header,
    HTTPException,
    Request,
    status,
)
from fastapi.middleware.cors import CORSMiddleware
from pydantic import EmailStr

from .base import Base
from .models import (  # TokenListRes,
    Credentials,
    InviteCode,
    InviteCodeListRes,
    MinimalInviteCode,
    MinimalOrganisation,
    NewInvitedUser,
    NewUser,
    Organisation,
    OrgListRes,
    OrgUpdateName,
    OrgUpdateOrgId,
    SignInRes,
    TokenListRes,
    TokenRes,
    TokenTester,
    UserInfo,
    UserListResponse,
    UserUpdateName,
    UserUpdatePassword,
    UserUpdateUserId,
)


class BaseAuth(Base, metaclass=ABCMeta):
    """
    base class for all auth modules of PaperText

    Attributes
    ----------
    TYPE: str
        type of module (the default is "AUTH" and shouldn't be changed)
    DEFAULTS: Dict[str, Any]
        python dict of default values for configuration (the default is {})
    requires_dir: bool
        default is False
        describes if directory for storage will be provide to __init__ call
    """

    TYPE: Final = "AUTH"

    public_org_id: str = "public"

    @staticmethod
    def add_CORS(api: FastAPI):  # noqa: N802
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
        * if greater_or_equal is non None: level_of_access >= greater_or_equal
        * if one_of is not None: level_of_access in one_of

        Parameters
        ----------
        greater_or_equal: int
            minimum level_of_access, i.e. tokens loa should be `>=` than greater_or_equal
        one_of: List[str]
            list of ints, tokens level_of_access should be `loa in one_of`

        Returns
        -------
        Callable[[str], UserInfo]
            function which accept `Authentication` header
            and returns info about tokens requester in UserInfos

        """
        if (greater_or_equal is not None) and (one_of is not None):
            raise ValueError(
                "greater_or_equal and one_of are provided, can accept only one"
            )

        if greater_or_equal is None and one_of is None:
            raise ValueError("either greater_or_equal or one_of should be provided")

        def return_function(x_authentication: str = Header(...)) -> UserInfo:
            # TODO: change to this in python3.9
            # token: str = x_authentication.removeprefix("Bearer: ")
            token: str = (
                x_authentication[8:]
                if x_authentication.startswith("Bearer: ")
                else x_authentication
            )

            user: UserInfo = UserInfo(**self.token2user(token))
            if greater_or_equal is not None:
                if user.level_of_access < greater_or_equal:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail={
                            "eng": "Users level_of_access "
                            f"({user.level_of_access}) is lower then "
                            f"required ({greater_or_equal})",
                            "rus": "Уровень доступа пользователся "
                            f"({user.level_of_access}) меньше чем "
                            f"необходимый ({greater_or_equal})",
                        },
                    )
            elif (one_of is not None) and (len(one_of) > 0):
                if user.level_of_access not in one_of:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail={
                            "eng": "Users level_of_access "
                            f"({user.level_of_access}) is not in "
                            f"required list ({one_of})",
                            "rus": "Уровень доступа пользователся "
                            f"({user.level_of_access}) не нахоится в "
                            f"списке необхрлимых ({one_of})",
                        },
                    )
            else:
                raise ValueError("invalid parameters")
            return user

        return return_function

    @abstractmethod
    def __init__(
        self,
        cfg: SimpleNamespace,
        storage_dir: Path,
    ):
        raise NotImplementedError

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
            user_id: str
            email: str
            member_of: str
            level_of_access: int
            user_name: str, optional
        """
        raise NotImplementedError

    @abstractmethod
    def cleanup_tokens(self):
        """
        will be added as job to BackgroundTasks on every signin
        should remove all expired tokens
        """
        raise NotImplementedError

    @abstractmethod
    async def signin(
        self,
        request: Request,
        password: str,
        identifier: Union[str, EmailStr],
    ) -> str:
        """
        checks identifier and password and returns new token

        Parameters
        ----------
        request: Request
        password: str
        identifier: Union[str, EmailStr]

        Returns
        -------
        str
            JSON Web Token
        """
        raise NotImplementedError

    @abstractmethod
    async def signup(
        self,
        request: Request,
        user_id: str,
        email: EmailStr,
        password: str,
        invitation_code: str,
        user_name: Optional[str] = None,
    ) -> str:
        """
        creates new user with given info if invite code exists

        Parameters
        ----------
        request: Request
        user_id: str
            new user_id of user, must be unique
        email: str
            email of new user, must be unique
        password: str
            password of new user
        invitation_code: str
            invitation code
        user_name: str, optional
            user_name of user

        Returns
        -------
        str
            JSON Web Token of created user
        """
        raise NotImplementedError

    # @abstractmethod
    # async def signout(self, token: str):
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
    async def signout_everywhere(self, user_id: str):
        """
        removes all tokens of current user

        Parameters
        ----------
        user_id: str
            user_id, whose tokens will be removed
        """
        raise NotImplementedError

    async def read_tokens(self, user_id: str) -> List[Dict[str, Any]]:
        """
        reads all tokens issued by user with id `user_id`

        Parameters
        ----------
        user_id: str
            id of user-owner of tokens
        """
        raise NotImplementedError

    @abstractmethod
    async def delete_token(self, token_identifier: str):
        """
        removes token

        Parameters
        ----------
        token_identifier: str
            token to remove
        """
        raise NotImplementedError

    # user

    @abstractmethod
    async def create_user(
        self,
        user_id: str,
        password: str,
        level_of_access: int = 0,
        email: Optional[EmailStr] = None,
        member_of: Optional[str] = None,
        user_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Creates user from provided info

        Parameters
        ----------
        user_id: str
            new users user_id
        email: str
            new users email
        password: str
            new users password
        level_of_access: int
            default: 0
            loa of new user
        member_of: str, optional
            organisation of user
            If none is provided then user will be in public org
        user_name: str, optional
            fullname of new user

        Returns
        -------
        Dict[str, Any]
            Contains:
                user_id: str
                email: str
                organisation: str
                level_of_access: int
                fullname: str, optional
        """
        raise NotImplementedError

    @abstractmethod
    async def read_user(self, user_id: str) -> Dict[str, Any]:
        """
        get information about user with given user_id

        Parameters
        ----------
        user_id: str
            user_id of user to delete

        Returns
        -------
        Dict[str, Union[str, int]]
            Contains:
                user_id: str
                email: str
                member_of: str
                level_of_access: int
                user_name: str, optional
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
            Contains:
                Dict[str, Union[str, int]]
                Contains:
                    user_id: str
                    email: str
                    member_of: str
                    level_of_access: int
                    user_name: str, optional
        """
        raise NotImplementedError

    @abstractmethod
    async def update_user(
        self,
        user_id: str,
        new_user_id: Optional[str] = None,
        new_user_name: Optional[str] = None,
        new_level_of_access: Optional[int] = None,
        new_organisation_id: Optional[str] = None,
    ) -> Dict[str, Union[str, int]]:
        """
        Updates user with given user_id

        Parameters
        ----------
        user_id: str
            user_id of user to delete
        new_user_id: str, optional
            default: None
            new user_id to replace previous
        new_user_name: str, optional
            default: None
            new user_name to replace previous
        new_level_of_access: int, optional
            default: None
            new level_of_access to replace previous
        new_organisation_id: str, optional
            default: None
            new organisation to replace previous

        Returns
        -------
        Dict[str, Union[str, int]]
            user object with new info
            Contains:
                user_id: str
                email: str
                member_of: str
                level_of_access: int
                user_name: str, optional
        """
        raise NotImplementedError

    @abstractmethod
    async def update_user_password(
        self,
        user_id: str,
        old_password: str,
        new_password: str,
    ) -> Dict[str, Union[str, int]]:
        """
        Updates user with given user_id

        Parameters
        ----------
        user_id: str
            user_id of user to delete
        old_password: str
            old password to check
        new_password: str
            new password to replace previous

        Returns
        -------
        Dict[str, Union[str, int]]
            user object with new info
            Contains:
                user_id: str
                email: str
                member_of: str
                level_of_access: int
                user_name: str, optional
        """
        raise NotImplementedError

    @abstractmethod
    async def update_user_email(
        self, user_id: str, new_email: EmailStr
    ) -> Dict[str, Union[str, int]]:
        """
        Updates user with given user_id

        Parameters
        ----------
        user_id: str
            user_id of user to delete
        new_email: EmailStr
            new email to replace previous

        Returns
        -------
        Dict[str, Union[str, int]]
            user object with new info
            Contains:
                user_id: str
                email: str
                member_of: str
                level_of_access: int
                user_name: str, optional
        """
        raise NotImplementedError

    @abstractmethod
    async def delete_user(self, user_id: str):
        """
        Removes user with given user_id

        Parameters
        ----------
        user_id: str
            user_id of user to delete
        """
        raise NotImplementedError

    # organisation

    @abstractmethod
    async def create_org(
        self,
        organisation_id: str,
        organisation_name: Optional[str] = None,
    ) -> Dict[str, Union[str, List[str]]]:
        """
        creates organisation with given name and title

        Parameters
        ----------
        organisation_id: str
        organisation_name: str, optional
            default: None
            name of new organisation

        Returns
        -------
        Dict[str, Union[str, List[str]]]
            new organisation
            Contains:
                member_of: str,
                organisation_name: str, optional
                users: List[str]
        """
        raise NotImplementedError

    @abstractmethod
    async def read_org(self, organisation_id: str) -> Dict[str, Union[str, List[str]]]:
        """
        returns info about organisation with given `member_of`

        Parameters
        ----------
        organisation_id: str
            id of organisation to return

        Returns
        -------
        Dict[str, Union[str, List[str]]]
            new organisation
            Contains:
                member_of: str
                organisation_name: str, optional
                users: List[str]
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
            Contains:
                Dict[str, str]
                    mapping from column to value, depends on `columns`
                    Contains:
                        member_of: str
                        organisation_name: str, optional
        """
        raise NotImplementedError

    @abstractmethod
    async def update_org(
        self,
        old_organisation_id: str,
        new_organisation_id: Optional[str] = None,
        new_organisation_name: Optional[str] = None,
    ) -> Dict[str, str]:
        """
        updates title of organisation with given name

        Parameters
        ----------
        old_organisation_id: str
            id of organisation
        new_organisation_id: str, optional
            new id of organisation
        new_organisation_name: str
            new name of organisation

        Returns
        -------
        Dict[str, str]
        new organisation
            Contains:
                member_of: str
                organisation_name: str, optional
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

    # invite codes

    @abstractmethod
    async def create_invite_code(
        self, issuer: str, code: str, add_to: str
    ) -> Dict[str, Any]:
        """
        creates invite code

        Parameters
        ----------
        issuer: str
            issuer of invite code
        code: str
        add_to: str
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
    async def delete_invite_code(self, code: str):
        """
        removes invite code

        Parameters
        ----------
        code: str
            invite code to remove
        """
        raise NotImplementedError

    def create_router(
        self,
        token_tester: TokenTester,
    ) -> APIRouter:
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
            "/signin",
            tags=["auth_module", "auth"],
            response_model=SignInRes,
        )
        async def signin(
            credentials: Credentials,
            request: Request,
            background_tasks: BackgroundTasks,
        ) -> SignInRes:
            """
            generates new token if provided user_id and password are correct
            """
            background_tasks.add_task(self.cleanup_tokens)
            return SignInRes(
                response=await self.signin(
                    request=request,
                    password=credentials.password,
                    identifier=credentials.identifier,
                )
            )

        @router.post(
            "/signup",
            tags=["auth_module", "auth"],
            response_model=SignInRes,
        )
        async def signup(
            user: NewInvitedUser,
            request: Request,
        ) -> SignInRes:
            """
            creates new user with provided
                user_id, password, name and invitation code
            """
            return SignInRes(response=await self.signup(request=request, **dict(user)))

        @router.get("/signout", tags=["auth_module", "auth"])
        async def signout(
            # requester: UserInfo = Depends(token_tester(greater_or_equal=0)),
            x_authentication: str = Header(...),
        ):
            """
            removes token from db of tokens
            """
            # x_authentication.removeprefix("Bearer: ")
            token: str = (
                x_authentication[7:]
                if x_authentication.startswith("Bearer: ")
                else x_authentication
            )
            await self.delete_token(token)

        @router.get("/signout_everywhere", tags=["auth_module", "auth"])
        async def signout_everywhere():
            """
            removes all tokens, associated with tokens user
            """
            raise NotImplementedError

        # tokens
        @router.get("/tokens", tags=["auth_module", "token"])
        async def read_tokens(
            requester: UserInfo = Depends(token_tester(greater_or_equal=0)),
        ) -> TokenListRes:
            """
            removes token by provided identifier:
                either token itself or token uuid
            """
            raw_tokens = await self.read_tokens(requester.user_id)
            tokens = [TokenRes(**dict(token)) for token in raw_tokens]
            return TokenListRes(response=tokens)

        @router.delete("/token", tags=["auth_module", "token"])
        async def delete_token(token_identifier: str = Body(...)):
            """
            removes token by provided identifier:
                either token itself or token uuid
            """
            await self.delete_token(token_identifier)

        # +-------+
        # | users |
        # +-------+
        @router.post(
            "/usrs",
            tags=["auth_module", "user", "access_level_2"],
            response_model=UserInfo,
        )
        async def create_user(user: NewUser) -> UserInfo:
            """
            creates user with provided user_id, password and user_name

            Note
            ----
            * created users are assigned to public organisation
            * created users loa is 1
            """
            created_user: Dict[str, Any] = await self.create_user(
                user_id=user.user_id,
                email=user.email,
                password=user.password,
                user_name=user.user_name,
            )
            return UserInfo(
                user_id=created_user["user_id"],
                email=created_user["email"],
                user_name=created_user["user_name"],
                member_of=created_user["member_of"],
                level_of_access=created_user["level_of_access"],
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
            "/usrs/{user_id}",
            tags=["auth_module", "user", "access_level_2"],
            response_model=UserInfo,
        )
        async def read_user(user_id: str) -> UserInfo:
            """
            return info about user with given user_id
            """
            user = await self.read_user(user_id)
            return UserInfo(
                user_id=user["user_id"],
                email=user["email"],
                user_name=user["user_name"],
                member_of=user["member_of"],
                level_of_access=user["level_of_access"],
            )

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
            raw_users: List[Dict[str, Any]] = await self.read_users()
            users: List[UserInfo] = [
                UserInfo(
                    user_id=user["user_id"],
                    email=user["email"],
                    user_name=user["user_name"],
                    member_of=user["member_of"],
                    level_of_access=user["level_of_access"],
                )
                for user in raw_users
            ]
            return UserListResponse(response=users)

        @router.patch(
            "/usrs/{user_id}/user_id",
            tags=["auth_module", "user", "access_level_2"],
        )
        async def update_users_user_id(
            user_id: str,
            new_user_id: UserUpdateUserId,
            requester: UserInfo = Depends(token_tester(greater_or_equal=2)),
        ):
            """
            changes user_id of user with given user_id
            """
            user: UserInfo = UserInfo(**(await self.read_user(user_id)))
            if requester.level_of_access == 3:
                pass
            elif user.level_of_access >= requester.level_of_access:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Can't edit user with higher or same privileges",
                )
            return await self.update_user(
                user_id=user_id, new_user_id=new_user_id.new_user_id
            )

        @router.patch(
            "/usr/{user_id}/password",
            tags=["auth_module", "user", "access_level_2"],
        )
        async def update_users_password(
            user_id: str,
            passwords: UserUpdatePassword,
            requester: UserInfo = Depends(token_tester(greater_or_equal=2)),
        ):
            """
            changes password of user with given user_id
            """
            user: UserInfo = UserInfo(**(await self.read_user(user_id)))
            if requester.level_of_access == 3:
                pass
            elif user.level_of_access >= requester.level_of_access:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Can't edit user with higher or same privileges",
                )
            await self.update_user_password(
                user_id=user_id,
                old_password=passwords.old_password,
                new_password=passwords.new_password,
            )

        @router.patch(
            "/usr/{user_id}/user_name",
            tags=["auth_module", "user", "access_level_2"],
        )
        async def update_users_fullname(
            user_id: str,
            new_fullname: UserUpdateName,
            requester: UserInfo = Depends(token_tester(greater_or_equal=2)),
        ):
            """
            changes user_name of user with given user_id
            """
            user: UserInfo = UserInfo(**(await self.read_user(user_id)))
            if requester.level_of_access == 3:
                pass
            elif user.level_of_access >= requester.level_of_access:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Can't edit user with higher or same privileges",
                )
            return await self.update_user(
                user_id=user_id, new_user_name=new_fullname.new_user_name
            )

        @router.post(
            "/usr/{user_id}/promote",
            tags=["auth_module", "user", "access_level_2"],
        )
        async def promote_user(
            user_id: str,
            requester: UserInfo = Depends(token_tester(greater_or_equal=1)),
        ):
            """
            increases loa of user with given user_id

            Note
            ----
            Maximum loa is equal to requesters loa
            """
            user: UserInfo = UserInfo(**(await self.read_user(user_id)))
            if requester.level_of_access == 3:
                pass
            elif user.level_of_access >= requester.level_of_access:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Can't edit user with higher or same privileges",
                )
            new_loa: int = min(user.level_of_access + 1, requester.level_of_access)
            return await self.update_user(user_id=user_id, new_level_of_access=new_loa)

        @router.post(
            "/usr/{user_id}/demote",
            tags=["auth_module", "user", "access_level_2"],
        )
        async def demote_user(
            user_id: str,
            requester: UserInfo = Depends(token_tester(greater_or_equal=1)),
        ):
            """
            decreases loa of user with given user_id

            Note
            ----
            Minimum loa is 0
            """
            user: UserInfo = UserInfo(**(await self.read_user(user_id)))
            if requester.level_of_access == 3:
                pass
            elif user.level_of_access >= requester.level_of_access:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Can't edit user with higher or same privileges",
                )
            new_loa: int = max(user.level_of_access - 1, requester.level_of_access)
            return await self.update_user(user_id=user_id, new_level_of_access=new_loa)

        @router.delete("/usr/{user_id}", tags=["auth_module", "user", "access_level_2"])
        async def delete_user(
            user_id: str,
            requester: UserInfo = Depends(token_tester(greater_or_equal=1)),
        ):
            """
            removes user, associated with user from token in request
            """
            user: UserInfo = UserInfo(**(await self.read_user(user_id)))
            if requester.level_of_access == 3:
                pass
            elif user.level_of_access >= requester.level_of_access:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Can't edit user with higher or same privileges",
                )
            await self.delete_user(user_id)

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
            "/orgs",
            tags=["auth_module", "organisation", "access_level_3"],
            dependencies=[Depends(token_tester(greater_or_equal=3))],
        )
        async def create_organisation(org: MinimalOrganisation):
            """
            creates new organisation with given org_id and name
            """
            await self.create_org(org.organisation_id, org.organisation_name)

        @router.get(
            "/orgs/{organisation_id}",
            tags=["auth_module", "organisation", "access_level_3"],
            response_model=Organisation,
            dependencies=[Depends(token_tester(greater_or_equal=3))],
        )
        async def read_organisation(organisation_id: str) -> Organisation:
            """
            returns info about organisation with given `org_id`
            """
            return Organisation(**(await self.read_org(organisation_id)))

        @router.patch(
            "/orgs/{organisation_id}/org_id",
            tags=["auth_module", "organisation", "access_level_2"],
            dependencies=[Depends(token_tester(greater_or_equal=2))],
        )
        async def update_org_organisation_id(
            organisation_id: str,
            new_org_id: OrgUpdateOrgId,
        ):
            """
            changes org_id of organisation to new_org_id
            """
            await self.update_org(
                organisation_id,
                new_organisation_id=new_org_id.new_organisation_id,
            )

        @router.patch(
            "/orgs/{organisation_id}/name",
            tags=["auth_module", "organisation", "access_level_2"],
            dependencies=[Depends(token_tester(greater_or_equal=2))],
        )
        async def update_org_name(
            org_id: str,
            new_name: OrgUpdateName,
        ):
            """
            changes name of organisation with given org_id to new_name
            """
            await self.update_org(
                org_id, new_organisation_name=new_name.new_organisation_name
            )

        @router.post(
            "/orgs/{organisation_id}/usrs",
            tags=["auth_module", "organisation", "access_level_3"],
            dependencies=[Depends(token_tester(greater_or_equal=3))],
        )
        async def create_user_in_org(
            organisation_id: str,
            user: NewUser,
        ):
            """
            creates user with provided user_id, password and user_name
            in organisation with given id

            Note
            ----
            * created users are assigned to requesters organisation
            * created users loa is 1
            """
            return await self.create_user(
                **dict(user),
                level_of_access=1,
                member_of=organisation_id,
            )

        @router.post(
            "/orgs/{organisation_id}/usrs/{user_id}",
            tags=["auth_module", "organisation", "access_level_3"],
        )
        async def add_user_to_org(
            organisation_id: str,
            user_id: str,
            requester: UserInfo = Depends(token_tester(greater_or_equal=3)),
        ):
            """
            adds user with provided user_id to organisation with given org_id
            if he is in public organisation
            """
            user: UserInfo = UserInfo(**(await self.read_user(user_id)))
            if requester.level_of_access == 3:
                pass
            elif user.level_of_access >= requester.level_of_access:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Can't edit user with higher or same privileges",
                )
            if user.member_of == "org:public":
                await self.update_user(user_id, new_organisation_id=organisation_id)
            else:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="can't invite user from non-public organisations",
                )

        @router.delete(
            "/orgs/{organisation_id}/usrs/{user_id}",
            tags=["auth_module", "organisation"],
        )
        async def delete_user_from_org(
            organisation_id: str,
            user_id: str,
            requester: UserInfo = Depends(token_tester(greater_or_equal=3)),
        ):
            """
            removes requested user
            """
            user: UserInfo = UserInfo(**(await self.read_user(user_id)))
            if requester.level_of_access == 3:
                pass
            elif user.level_of_access >= requester.level_of_access:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Can't edit user with higher or same privileges",
                )
            if user.member_of != "org:public":
                await self.update_user(user_id, new_organisation_id=organisation_id)
            else:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="can't remove user from public organisations",
                )

        @router.delete(
            "/orgs/{organisation_id}",
            tags=["auth_module", "organisation", "access_level_3"],
            dependencies=[Depends(token_tester(greater_or_equal=3))],
        )
        async def delete_organisation(organisation_id: str):
            """
            removes organisation with given name
            """
            return await self.delete_org(organisation_id)

        # +---------+
        # | Invites |
        # +---------+

        @router.post(
            "/invites",
            tags=["auth_module", "invite", "access_level_1"],
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
                if invite_code.add_to not in [
                    self.public_org_id,
                    requester.member_of,
                ]:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="can't invite to non-user or non-public organisation",
                    )
            return await self.create_invite_code(
                requester.user_id, invite_code.code, invite_code.add_to
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
            codes: List[InviteCode] = [InviteCode(**code) for code in raw_codes]
            if requester.level_of_access == 3:
                # admin
                return InviteCodeListRes(response=codes)
            elif requester.level_of_access == 2:
                # organizer
                new_codes: List[InviteCode] = []
                for code in codes:
                    user: UserInfo = UserInfo(**(await self.read_user(code.issuer_id)))
                    if (
                        user.member_of == requester.member_of
                        or user.user_id == requester.user_id
                        or code.add_to == self.public_org_id
                    ):
                        new_codes.append(code)
                return InviteCodeListRes(response=new_codes)
            else:
                # anyone else
                new_codes: List[InviteCode] = []
                for code in codes:
                    user: UserInfo = UserInfo(**(await self.read_user(code.issuer_id)))
                    if (
                        user.user_id == requester.user_id
                        or code.add_to == self.public_org_id
                    ):
                        new_codes.append(code)
                return InviteCodeListRes(response=new_codes)

        @router.get(
            "/invites/{invite_code}",
            tags=["auth_module", "invite", "access_level_1"],
            response_model=InviteCode,
        )
        async def read_invite_code(
            invite_code: str,
        ) -> InviteCode:
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
            "/invites/{invite_code}",
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

            await self.delete_invite_code(invite_code)

        self.add_routes(router, token_tester)
        return router
