from typing import List
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from paperback.auth import models, orm
from paperback.auth.hash import crypto_context


async def get_user(session: AsyncSession, user_uuid: uuid4) -> models.User:
    result = await session.execute(
        select(orm.User).filter(models.User.user_uuid == user_uuid)
    )
    return result.scalars().first()


async def get_user_by_email(session: AsyncSession, email: str) -> models.User:
    result = await session.execute(select(orm.User).filter(models.User.email == email))
    return result.scalars().first()


async def get_users(session: AsyncSession) -> List[models.User]:
    return (await session.execute(select(orm.User))).fetchall()


async def create_user(session: AsyncSession, user: models.UserCreate) -> models.User:
    hashed_password = crypto_context.hash(user.password)
    db_user = orm.User(
        username=user.username,
        hashed_password=hashed_password,
        level_of_access=1,
        email=user.email,
    )

    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)
    return models.User(**dict(db_user))
