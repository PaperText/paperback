from functools import lru_cache

from pydantic import BaseSettings, Field


class AuthSettings(BaseSettings):
    db_user: str
    db_pass: str
    db_host: str
    db_port: str = "5432"
    db_name: str = "auth_module"

    class Config:
        env_prefix = "auth__"


@lru_cache()
def get_settings():
    return AuthSettings()
