import uuid
from typing import List, Dict, Any
from uuid import uuid4


from sqlalchemy.future import select
from sqlalchemy.orm import Session

from paperback.auth import schemas, orm
from paperback.auth.logging import logger
from paperback.auth.hash import crypto_context


def get_user(session: Session, user_uuid: uuid4) -> schemas.User:
    res = session.execute(
        select(orm.User).filter(orm.User.user_uuid == user_uuid)
    ).scalars().first()
    return res


def get_user_by_email(session: Session, email: str) -> schemas.User:
    res = session.execute(select(orm.User).filter(orm.User.email == email)).scalars().first()
    return res


def get_users(session: Session) -> List[schemas.User]:
    res = session.execute(select(orm.User))
    return res.scalars().all()


def create_user(session: Session, user: schemas.UserCreate) -> schemas.User:
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
    return schemas.User(**dict(db_user))


def get_token(session: Session, token_uuid: uuid4) -> schemas.Token:
    res = session.execute(
        select(orm.Token).filter(schemas.Token.token_uuid == token_uuid)
    ).scalars().first()
    return res


def get_user_by_token_uuid(session: Session, token_uuid: uuid4) -> schemas.User:
    res = session.execute(
        select(orm.Token).filter(schemas.Token.token_uuid == token_uuid)
    ).scalars().first().user
    return res
