from typing import Any

from fastapi import FastAPI
from starlette.responses import JSONResponse

from .__version__ import __version__

default_response_class: Any

try:
    from fastapi.responses import ORJSONResponse

    default_response_class = ORJSONResponse
except Exception:
    pass
    # maybe notify about optional dependency?

default_response_class = JSONResponse


api = FastAPI(
    title="PaperText backend [Paperback]",
    description="Backend API for PaperText",
    version=__version__,
    openapi_tags=[
        {"name": "auth", "description": "authorization"},
        {"name": "token", "description": "token manipulation"},
        {"name": "user", "description": "users manipulation"},
        {"name": "organisation", "description": "organisation manipulation"},
        {"name": "invite", "description": "invite codes manipulation"},
        {"name": "docs", "description": "document manipulation"},
        {"name": "corps", "description": "corpus manipulation"},
        {"name": "dict", "description": "dictionaries manipulation"},
        {"name": "analyzer", "description": "analyzer usage"},
    ]
    + [
        {
            "name": f"access_level_{i}",
            "description": f"paths that require level {i} access",
        }
        for i in range(4)
    ],
    docs_url="/documentation",
    redoc_url="/re_documentation",
    default_response_class=default_response_class,
)
