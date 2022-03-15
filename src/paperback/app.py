import logging
from logging.handlers import RotatingFileHandler
import os
import time
from pathlib import Path
from typing import List, Callable, Dict, Any, Set, Union
from copy import deepcopy

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

import uuid

from paperback import __version__
from paperback.auth.router import auth_router
from paperback.docs.router import docs_router
from paperback.util import get_response_class
from paperback.settings import get_settings

from uvicorn.logging import ColourizedFormatter

# from pkg_resources import iter_entry_points

# global settings
settings = get_settings()
config_dir = Path(settings.config_dir).resolve()

# setup root logger
root_logger = logging.getLogger()
root_logger.setLevel(settings.log_level)

logs_dir = config_dir / "logs"
if logs_dir.exists() and logs_dir.is_dir():
    root_logger.debug("found logging folder")
else:
    root_logger.debug("can't find logging folder, creating it")
    logs_dir.mkdir(parents=True)
    root_logger.debug("created logging folder")

# file handler
logging_file_handler = RotatingFileHandler(
    logs_dir / "root.log",
    maxBytes=1024 ** 3,
    backupCount=20,
)
logging_file_handler.setFormatter(
    logging.Formatter(
        "{levelname:<8} in {name:<16} at {asctime:<16}: {message}",
        "%Y-%m-%d %H:%M:%S",
        style="{",
    )
)
root_logger.addHandler(logging_file_handler)

# console handler
logging_console_handler = logging.StreamHandler()
logging_console_handler.setFormatter(
    ColourizedFormatter(
        "{levelprefix:<8} @ {name:<10} : {message}",
        "%Y-%m-%d %H:%M:%S",
        style="{",
        use_colors=True,
    )
)
root_logger.addHandler(logging_console_handler)

# setup paperback logger
logger = logging.getLogger("paperback")

# create app
logger.info("initializing PaperBack app")

app = FastAPI(
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
    docs_url="/spec",
    redoc_url="/re_spec",
    default_response_class=get_response_class(),
)

# adding default routers

logger.info("adding default routers")

logger.debug("adding auth routers")
app.include_router(auth_router)

logger.debug("adding docs routers")
app.include_router(docs_router)

# adding middleware

logger.info("adding middleware")

logger.debug("adding CORS middleware")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger.debug("adding process time middleware")


@app.middleware("http")
async def add_process_time_header(request: Request, call_next: Callable):
    start_time: float = time.time()
    response = await call_next(request)
    process_time: float = time.time() - start_time
    process_time = round(process_time, 2)
    process_time_str: str = str(process_time) + " seconds"
    response.headers["X-Process-Time"] = process_time_str
    return response


# default routes

logger.info("adding default routes")

logger.debug("adding /info path")


@app.get("/info", tags=["root"])
def stats():
    """basic app info"""
    return {
        "version": __version__,
        "is_uuid_safe": str(uuid.uuid4().is_safe).split(".")[-1],
    }
