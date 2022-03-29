import asyncio

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from paperback.auth.settings import get_settings

settings = get_settings()

engine = create_async_engine(
    f"postgresql+asyncpg://{settings.db_user}:{settings.db_pass}@{settings.db_host}:{settings.db_port}/{settings.db_name}",
    future=True,
)
async_session = sessionmaker(
    engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
    class_=AsyncSession,
    future=True,
)

Base = declarative_base()
