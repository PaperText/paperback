import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from paperback.auth.database import engine, Base, async_session
from paperback.auth import models, crud
from paperback.auth.settings import get_settings

auth_router = APIRouter()

logger = logging.getLogger("paperback.auth")


# Dependency
async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session


def token_tester():
    pass


def check_credentials(credentials: models.Credentials):
    pass


@auth_router.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@auth_router.get("/user", tags=["auth"], response_model=List[models.User])
async def get_users(session=Depends(get_session)) -> List[models.User]:
    """
    generates new token if provided user_id and password are correct
    """
    return await crud.get_users(session)
