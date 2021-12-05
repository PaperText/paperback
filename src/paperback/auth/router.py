from fastapi import APIRouter, Depends, HTTPException, status

from paperback.auth.settings import get_settings
from paperback.auth.models import Credentials

auth_router = APIRouter()


def token_tester():
    pass


def check_credentials(credentials: Credentials):
    pass


@auth_router.post(
    "/signin",
    tags=["auth"],
    response_model=str
)
async def signin(
    credentials: Credentials,
    check_credentials=Depends(check_credentials)
) -> str:
    """
    generates new token if provided user_id and password are correct
    """
    if check_credentials(credentials):
        return None
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


@auth_router.post(
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


@auth_router.get("/signout", tags=["auth_module", "auth"])
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


@auth_router.get("/signout_everywhere", tags=["auth_module", "auth"])
async def signout_everywhere():
    """
    removes all tokens, associated with tokens user
    """
    raise NotImplementedError


# tokens
@auth_router.get("/tokens", tags=["auth_module", "token"])
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


@auth_router.delete("/token", tags=["auth_module", "token"])
async def delete_token(token_identifier: str = Body(...)):
    """
    removes token by provided identifier:
        either token itself or token uuid
    """
    await self.delete_token(token_identifier)


# +-------+
# | users |
# +-------+
@auth_router.post(
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


@auth_router.get(
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


@auth_router.get(
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


@auth_router.get(
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


@auth_router.patch(
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


@auth_router.patch(
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


@auth_router.patch(
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


@auth_router.post(
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


@auth_router.post(
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


@auth_router.delete("/usr/{user_id}", tags=["auth_module", "user", "access_level_2"])
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
@auth_router.get(
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


@auth_router.post(
    "/orgs",
    tags=["auth_module", "organisation", "access_level_3"],
    dependencies=[Depends(token_tester(greater_or_equal=3))],
)
async def create_organisation(org: MinimalOrganisation):
    """
    creates new organisation with given org_id and name
    """
    await self.create_org(org.organisation_id, org.organisation_name)


@auth_router.get(
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


@auth_router.patch(
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


@auth_router.patch(
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


@auth_router.post(
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


@auth_router.post(
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


@auth_router.delete(
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


@auth_router.delete(
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

@auth_router.post(
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


@auth_router.get(
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


@auth_router.get(
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

@auth_router.delete(
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
