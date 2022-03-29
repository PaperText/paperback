from functools import lru_cache
from pathlib import Path

from pydantic import BaseSettings

# from paperback.auth.settings import AuthSettings, get_auth_settings
# from paperback.docs.settings import DocsSettings, get_docs_settings


class AppSettings(BaseSettings):
    log_level: str = "INFO"
    config_dir: Path = Path.home() / ".papertext"


@lru_cache()
def get_settings():
    return AppSettings()
