import datetime
import uuid
from typing import List, Optional, Dict, Any, cast, Iterator

from authlib.jose import jwt, errors as jwt_errors
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
    Header,
    Request,
    BackgroundTasks,
    Body,
)
from pydantic import EmailStr
from email_validator import validate_email, EmailNotValidError
from sqlalchemy.orm import Session

from paperback.settings import (
    get_settings as get_root_settings,
    AppSettings as RootSettings,
)

from paperback.auth.database import engine, Base, local_session, get_session
from paperback.auth.hash import crypto_context
from paperback.auth.jwt import get_decode_token, get_jwt_keys, JWTKeys, claim_option
from paperback.auth import schemas, crud, orm
from paperback.auth.logging import logger
from paperback.auth.settings import AuthSettings, get_auth_settings

auth_router = APIRouter()


def get_level_of_access(
    greater_or_equal: int | None = None,
    one_of: list[int] | None = None,
):
    if (greater_or_equal is not None) and (one_of is not None):
        raise ValueError(
            "greater_or_equal and one_of are provided, can accept only one"
        )

    if greater_or_equal is None and one_of is None:
        raise ValueError("either greater_or_equal or one_of should be provided")

    def return_function(
        x_authentication: str = Header(...),
        decode_token=Depends(get_decode_token),
        session=Depends(get_session),
    ) -> schemas.Token:
        token: str = x_authentication.removeprefix("Bearer: ")

        token: schemas.Token = decode_token(token)

        user = token.user
        if greater_or_equal is not None:
            if user.level_of_access < greater_or_equal:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Users level_of_access "
                    f"({user.level_of_access}) is lower then "
                    f"required ({greater_or_equal})",
                )
        elif (one_of is not None) and (len(one_of) > 0):
            if user.level_of_access not in one_of:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Users level_of_access "
                    f"({user.level_of_access}) is not in "
                    f"required list ({one_of})",
                )

        return token

    return return_function


@auth_router.on_event("startup")
async def startup():
    """
    Note
    ----
    this won't work in testing as id doesn't account overrides
    """
    settings = get_auth_settings()
    logger.debug("settings on startup of auth module: %s", settings)

    logger.debug("creating ORM classes")
    orm.Base.metadata.create_all(bind=engine)
    # with engine.begin() as conn:
    #     await conn.run_sync(Base.metadata.create_all)

    match settings:
        case AuthSettings(
            create_root_user=True, root_user_password=root_user_password
        ) if root_user_password is not None:
            logger.debug("trying to create root user")

            session = next(get_session())

            logger.debug("getting root user")
            root_user = crud.get_user_by_username(session, "root")
            if root_user is None:
                logger.debug("can't find root user, creating it")
                root_user = schemas.UserCreate(
                    username="root",
                    password=root_user_password,
                )
                logger.debug("root user to create: %s", root_user)
                crud.create_user(session, root_user)
            else:
                logger.debug("found root user: %s", root_user)
                if not crypto_context.verify(
                    root_user_password, root_user.hashed_password
                ):
                    logger.error("root user already exists, but password is incorrect")
                    raise Exception(
                        "root user already exists, but password is incorrect"
                    )
        case AuthSettings(
            create_root_user=False, root_user_password=root_user_password
        ) if root_user_password is not None:
            logger.error(
                "`create_root_user` is set to `False`, but `root_user_password` is provided"
            )
        case AuthSettings(
            create_root_user=True, root_user_password=root_user_password
        ) if root_user_password is None:
            logger.error(
                "`create_root_user` is set to `True`, but `root_user_password` is not provided"
            )


@auth_router.post("/signin", tags=["auth"], response_model=str)
async def signin(
    credentials: schemas.Credentials,
    background_tasks: BackgroundTasks,
    session: Session = Depends(get_session),
    jwt_keys: JWTKeys = Depends(get_jwt_keys),
) -> str:
    """
    generates new token if provided user_id and password are correct
    """
    logger.debug("logging in user with identifier %s", credentials.identifier)
    try:
        validated_email = validate_email(credentials.identifier)
        email = validated_email.email
        user = crud.get_user_by_email(session, email)
    except EmailNotValidError:
        username = credentials.identifier
        user = crud.get_user_by_username(session, username)

    if not crypto_context.verify(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password",
        )
    else:
        logger.debug("password of user %s was correct", user)

    now = datetime.datetime.now()

    new_token = schemas.CreateToken(
        issued_at=now,
        user_uuid=user.user_uuid,
    )
    token = crud.create_token(session, new_token)

    header: dict[str, str] = {"alg": "ES384", "typ": "JWT"}
    payload: dict[str, str | int] = {
        "iss": "paperback",
        "sub": str(token.user_uuid),
        "exp": int(round((now + datetime.timedelta(days=2)).timestamp(), 0)),
        "iat": int(round(now.timestamp(), 0)),
        "jti": str(token.token_uuid),
    }
    encoded_jwt = jwt.encode(header, payload, jwt_keys["private_key"])
    return encoded_jwt


@auth_router.post("/signup", tags=["auth"], response_model=schemas.UserOut)
async def signup(
    new_user: schemas.UserCreate, session=Depends(get_session)
) -> orm.User:
    """
    creates new user with specified info
    """
    logger.debug("creating new user: %s", new_user)
    user = crud.create_user(session, new_user)
    return user


@auth_router.get("/signout", tags=["auth"])
async def signout(
    token: orm.Token = Depends(get_level_of_access(greater_or_equal=0)),
    session=Depends(get_session),
):
    """
    removes token used for execution from database
    """
    crud.delete_token(session, token.token_uuid)


@auth_router.get("/signout_everywhere", tags=["auth"])
async def signout_everywhere(
    token: orm.Token = Depends(get_level_of_access(greater_or_equal=0)),
    session=Depends(get_session),
):
    """
    removes token used for execution from database
    """
    user = token.user
    logger.debug("deleting tokens of user %s", user)
    tokens = user.tokens
    logger.debug("tokens to delete: %s", tokens)
    for t in tokens:
        crud.delete_token(session, t.token_uuid)

# tokens


@auth_router.get("/tokens", tags=["token"], response_model=list[schemas.TokenOut])
async def get_tokens(
    token: orm.Token = Depends(get_level_of_access(greater_or_equal=0)),
) -> list[orm.Token]:
    """
    returns all tokens of requester
    """
    return token.user.tokens


@auth_router.delete("/tokens", tags=["token"])
async def delete_tokens(
    token_identifier: str = Body(..., description="token itself of uuid of token"),
    jwt_keys: JWTKeys = Depends(get_jwt_keys),
    session=Depends(get_session),
    token: orm.Token = Depends(get_level_of_access(greater_or_equal=0)),
):
    """
    removes specified token
    """
    try:
        claims = jwt.decode(token, jwt_keys["public_key"], claim_option=claim_option)
        claims.validate()
        token_uuid = claims["jti"]
    except jwt_errors.DecodeError:
        token_uuid = token
    crud.delete_token(session, token_uuid)

# users


@auth_router.get("/me", tags=["user"], response_model=schemas.UserOut)
async def get_me(
    token: orm.Token = Depends(get_level_of_access(greater_or_equal=0)),
):
    """
    returns current user
    """
    return token.user


@auth_router.get("/user", tags=["user"], response_model=list[schemas.UserOut], deprecated=True)
async def get_users(
    token: orm.Token = Depends(get_level_of_access(greater_or_equal=3)),
):
    """
    reads all existing users
    """
    raise NotImplementedError


@auth_router.post("/user", tags=["user"], response_model=schemas.UserOut, deprecated=True)
async def create_user(
    user: schemas.UserCreate,
):
    """
    creates user with provided user_id, password and user_name

    Note
    ----
    * created users are assigned to public organisation
    * created users loa is 1

    """
    raise NotImplementedError


@auth_router.get("/user/{username}", tags=["user"], response_model=schemas.UserOut, deprecated=True)
async def get_user_by_username(
    username: str,
    token: orm.Token = Depends(get_level_of_access(greater_or_equal=0)),
):
    """
    return info about user with given username
    """
    raise NotImplementedError


@auth_router.patch("/user/{username}/promote", tags=["user"], response_model=schemas.UserOut, deprecated=True)
async def promote_user_by_username(
    username: str,
    token: orm.Token = Depends(get_level_of_access(greater_or_equal=0)),
):
    """
    promotes (increases loa) user with given username
    """
    raise NotImplementedError


@auth_router.patch("/user/{username}/demote", tags=["user"], response_model=schemas.UserOut, deprecated=True)
async def demote_user_by_username(
    username: str,
    token: orm.Token = Depends(get_level_of_access(greater_or_equal=0)),
):
    """
    demotes (decreases loa) user with given username
    """
    raise NotImplementedError


@auth_router.patch("/user/{username}/password", tags=["user"], response_model=schemas.UserOut, deprecated=True)
async def update_password_of_user_by_username(
    username: str,
    token: orm.Token = Depends(get_level_of_access(greater_or_equal=0)),
):
    """
    updates password of user with given username
    """
    raise NotImplementedError


@auth_router.delete("/user/{username}", tags=["user"], response_model=schemas.UserOut, deprecated=True)
async def delete_user_by_username(
    username: str,
    token: orm.Token = Depends(get_level_of_access(greater_or_equal=0)),
):
    """
    removes user with given username
    """
    raise NotImplementedError
