from functools import lru_cache

from pydantic import BaseSettings


class DocsSettings(BaseSettings):
    test: bool = False

    class Config:
        env_prefix = "docs_"


@lru_cache()
def get_settings():
    return DocsSettings()
