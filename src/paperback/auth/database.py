import asyncio
from typing import Iterator

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker

from paperback.auth.settings import get_auth_settings

settings = get_auth_settings()

engine = create_engine(
    f"postgresql+psycopg2://{settings.db_user}:{settings.db_pass}@{settings.db_host}:{settings.db_port}/{settings.db_name}",
    future=True,
)
local_session = sessionmaker(
    engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
    future=True,
)

Base = declarative_base()


# Dependency
def get_session() -> Iterator[Session]:
    session = local_session()
    try:
        yield session
    finally:
        session.close()
