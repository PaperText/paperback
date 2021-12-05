import asyncio

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from paperback.auth.settings import get_settings

settings = get_settings()

engine = create_async_engine(settings.database_url)
async_session = sessionmaker(engine, autocommit=False, autoflush=False, class_=AsyncSession)

Base = declarative_base()
