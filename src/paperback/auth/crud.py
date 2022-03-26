import uuid
from datetime import datetime
from typing import Any, Dict, List
from uuid import uuid4

from sqlalchemy import inspect
from sqlalchemy.future import select
from sqlalchemy.orm import Session

from paperback.auth import orm, schemas
from paperback.auth.hash import crypto_context
from paperback.auth.logging import logger


def get_user(session: Session, user_uuid: uuid4) -> orm.User:
    res = (
        session.execute(select(orm.User).filter(orm.User.user_uuid == user_uuid))
        .scalars()
        .first()
    )
    return res


def get_user_by_username(session: Session, username: str) -> orm.User:
    res = (
        session.execute(select(orm.User).filter(orm.User.username == username))
        .scalars()
        .first()
    )
    return res


def get_user_by_email(session: Session, email: str) -> orm.User:
    res = (
        session.execute(select(orm.User).filter(orm.User.email == email))
        .scalars()
        .first()
    )
    return res


def get_users(session: Session) -> List[orm.User]:
    res = session.execute(select(orm.User)).scalars().all()
    return [r for r in res]


def create_user(session: Session, user: schemas.UserCreate) -> orm.User:
    hashed_password = crypto_context.hash(user.password)
    db_user = orm.User(
        username=user.username,
        hashed_password=hashed_password,
        level_of_access=1,
        email=user.email,
    )

    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


def get_token(session: Session, token_uuid: uuid4) -> orm.Token:
    res = (
        session.execute(select(orm.Token).filter(orm.Token.token_uuid == token_uuid))
        .scalars()
        .first()
    )
    return res


def delete_token(session: Session, token_uuid: uuid4):
    session.delete(get_token(session, token_uuid))
    session.commit()


def create_token(session: Session, token: schemas.CreateToken) -> orm.Token:
    db_token = orm.Token(
        issued_at=token.issued_at,
        user_uuid=token.user_uuid,
    )

    session.add(db_token)
    session.commit()
    session.refresh(db_token)
    logger.debug("created token: %s", db_token)
    logger.debug("user in created token: %s", db_token.user)
    return db_token
