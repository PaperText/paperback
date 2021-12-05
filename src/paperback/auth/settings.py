from functools import lru_cache

from pydantic import BaseSettings


class AuthSettings(BaseSettings):
    database_url: str

    class Config:
        env_prefix = "auth_"


@lru_cache()
def get_settings():
    return AuthSettings()
