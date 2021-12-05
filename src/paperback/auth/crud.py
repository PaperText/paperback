from sqlalchemy.ext.asyncio import AsyncSession

from paperback.auth import models, orm
from paperback.auth.crypto import crypto_context


def get_user(db: AsyncSession, user_id: str):
    return db.query(models.User).filter(models.User.user_id == user_id).first()


def get_user_by_email(db: AsyncSession, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def get_users(db: AsyncSession):
    return db.query(models.User).all()


def create_user(db: AsyncSession, user: models.UserCreate) -> models.User:
    hashed_password = crypto_context.hash(user.password)
    db_user = models.User(email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return models.User(**dict(db_user))


