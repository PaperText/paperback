from functools import lru_cache

from pydantic import BaseSettings


class DocsSettings(BaseSettings):
    db_scheme: str = "bolt"
    db_user: str = "neo4j"
    db_pass: str = "password"
    db_host: str = "localhost"
    db_port: str = "7687"

    analyzers_titanis_host: str | None

    analyzers_pyexling_host: str | None
    analyzers_pyexling_service: str | None

    class Config:
        env_prefix = "docs__"


@lru_cache()
def get_docs_settings():
    docs_settings = DocsSettings()

    if (
        docs_settings.analyzers_pyexling_host is None
        or docs_settings.analyzers_pyexling_service is None
    ):
        raise ValueError(
            "Docs settings: can't start without pyexling configuration "
            "please specify `analyzers_pyexling_host` and `analyzers_pyexling_service`"
        )

    if docs_settings.analyzers_titanis_host is None:
        raise ValueError(
            "Docs settings: can't start without titanis configuration "
            "please specify `analyzers_titanis_host`"
        )

    return docs_settings
