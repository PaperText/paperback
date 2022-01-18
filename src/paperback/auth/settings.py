from functools import lru_cache
from pathlib import Path

from pydantic import BaseSettings, Field


class AuthSettings(BaseSettings):
    db_user: str
    db_pass: str
    db_host: str
    db_port: str = "5432"
    db_name: str = "auth_module"

    storage_path: Path

    recreate_keys: bool = False
    curve: str = "secp521r1"

    class Config:
        env_prefix = "auth__"


@lru_cache()
def get_auth_settings():
    auth_settings = AuthSettings()

    # storage path
    auth_settings.storage_path = Path(auth_settings.storage_path).resolve()
    if not auth_settings.storage_path.exists():
        auth_settings.storage_path.mkdir(parents=True, exist_ok=True)
    else:
        if not auth_settings.storage_path.is_dir():
            raise Exception("Auth settings: storage path exists, but isn't a dir")

    return auth_settings
