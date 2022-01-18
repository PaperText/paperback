from typing import List, Optional, Dict, Any

from fastapi import APIRouter, Depends, HTTPException, status, Header, Request, BackgroundTasks
from paperback.settings import (
    get_settings as get_root_settings,
    AppSettings as RootSettings,
)
from paperback.auth.database import engine, Base, local_session, get_session
from paperback.auth.jwt import get_decode_token
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
        session=Depends(get_session)
    ) -> schemas.Token:
        # TODO: change to this in python3.9
        # token: str = x_authentication.removeprefix("Bearer: ")
        token: str = (
            x_authentication[8:]
            if x_authentication.startswith("Bearer: ")
            else x_authentication
        )

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
    logger.debug("creating ORM classes")
    orm.Base.metadata.create_all(bind=engine)
    # with engine.begin() as conn:
    #     await conn.run_sync(Base.metadata.create_all)


@auth_router.get("/signin", tags=["auth"], response_model=str)
async def signin(
    credentials: schemas.Credentials,
    request: Request,
    background_tasks: BackgroundTasks,
) -> str:
    """
    generates new token if provided user_id and password are correct
    """
    return "token"


# TODO: remove

@auth_router.get("/user", tags=["auth"], response_model=list[schemas.User])
async def get_users(session=Depends(get_session)) -> list[schemas.User]:
    """
    generates new token if provided user_id and password are correct
    """
    return crud.get_users(session)


@auth_router.get("/test", tags=["auth"], response_model=schemas.User)
async def test(user: schemas.User = Depends(get_level_of_access(greater_or_equal=1))) -> schemas.User:
    """
    generates new token if provided user_id and password are correct
    """
    return user
