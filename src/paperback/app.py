import logging
from logging.handlers import RotatingFileHandler
import os
import time
from pathlib import Path
from typing import List, Callable, Dict, Any, Set, Union
from copy import deepcopy

from fastapi import FastAPI, Request
import uuid

from paperback import __version__
from paperback.std import AuthImplemented, DocsImplemented
from paperback.util import get_response_class
from paperback.settings import get_settings
from uvicorn.logging import ColourizedFormatter
from pkg_resources import iter_entry_points
from paperback.abc import BaseAuth, BaseDocs, BaseMisc, Base
from paperback.exceptions import DuplicateModuleError, InheritanceError

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
    default_response_class=get_response_class(),
)

# global settings

config_dir = Path(os.environ.get("PT__config_dir", Path.home() / ".papertext")).resolve()
log_level = os.environ.get("PT__log_level", "")

# setup logging
root_logger = logging.getLogger()

logger = logging.getLogger("paperback")
logger.setLevel(log_level)

## set temporary console only logging
tmp_stream_handler = logging.StreamHandler()
tmp_stream_handler.setLevel("DEBUG")
root_logger.addHandler(tmp_stream_handler)
logger.debug("temporary console-only logger was set up")

## check that folder for logs exists
logger.debug("checking for logging folder")
logs_dir = config_dir / "logs"
if logs_dir.exists() and logs_dir.is_dir():
    logger.debug("found logging folder")
else:
    logger.debug("can't find logging folder, creating it")
    logs_dir.mkdir(parents=True)
    logger.debug("created logging folder")

## configure propper logging
logger.debug("configuring logger")
root_logger.removeHandler(tmp_stream_handler)

### file handler
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
logging_file_handler.setLevel("DEBUG")
root_logger.addHandler(logging_file_handler)

### console handler
logging_console_handler = logging.StreamHandler()
logging_console_handler.setFormatter(
    ColourizedFormatter(
        "{levelprefix:<8} @ {name:<10} : {message}",
        "%Y-%m-%d %H:%M:%S",
        style="{",
        use_colors=True,
    )
)
logging_console_handler.setLevel(log_level)
root_logger.addHandler(logging_console_handler)

# create app
logger.info("initializing PaperBack app")

## search plugins
names: Set[str] = set()
plugin_type2class: Dict[str, List[Any]] = {
    "AUTH": [],
    "DOCS": [],
    "MISC": [],
}
cls2name: Dict[Any, str] = {}

for entry_point in iter_entry_points("paperback.modules"):
    name = entry_point.name
    logger.debug("found %s plugin", name)

    # load class and check that it's correct type and it's name is appropriate
    cls: Union[Any, BaseMisc, BaseAuth, BaseDocs] = entry_point.load()

    if not any(
        issubclass(cls, class_i) for class_i in [BaseMisc, BaseAuth, BaseDocs]
    ):
        logger.error(
            "plugin %s doesn't inherit from BaseMisc, BaseAuth or BaseDocs",
            name,
        )
        raise InheritanceError(
            f"module {name} doesn't inherit from BaseMisc, BaseAuth or BaseDocs"
        )

    if cls.TYPE == "AUTH":
        if name != "auth":
            logger.warning(
                "`AUTH` module has incorrect name `%s`, changing to `auth`",
                name,
            )
            name = "auth"
    elif cls.TYPE == "DOCS":
        if name != "docs":
            logger.warning(
                "`DOCS` module has incorrect name `%s`, changing to `docs`",
                name,
            )
            name = "docs"
    elif cls.TYPE == "MISC":
        pass
    else:
        raise ValueError(f"Unsupported class type {cls.TYPE} of plugin {name}")

    if name in names:
        logger.error(
            "plugin with name `%s` already exists, but should be unique",
            name,
        )
        raise ValueError(
            f"plugin with name `{name}` already exists, but should be unique"
        )
    else:
        names.add(name)

    plugin_type2class[cls.TYPE].append(cls)
    cls2name[cls] = name

### ensure only one AUTH and DOCS plugin is loaded
### if no AUTH or DOCS plugins - load from std

len_auth_modules = len(plugin_type2class["AUTH"])
if len_auth_modules == 0:
    logger.debug("no auth modules were detected, using standard implementation")
    plugin_type2class["AUTH"].append(AuthImplemented)
    cls2name[AuthImplemented] = "auth"
    names.add("auth")
elif len_auth_modules == 1:
    pass
else:
    logger.error("too many (%s) auth modules were detected", len_auth_modules)
    raise DuplicateModuleError(
        f"too many ({len_auth_modules}) auth modules were detected"
    )

len_docs_modules = len(plugin_type2class["DOCS"])
if len_docs_modules == 0:
    logger.debug("no docs modules were detected, using standard implementation")
    plugin_type2class["DOCS"].append(DocsImplemented)
    cls2name[DocsImplemented] = "docs"
    names.add("docs")
elif len_docs_modules == 1:
    pass
else:
    logger.error("too many (%s) docs modules were detected", len_docs_modules)
    raise DuplicateModuleError(
        f"too many ({len_docs_modules}) docs modules were detected"
    )

## organize plugins
plugin_name2cls: Dict[str, Any] = {}
plugin_name2settings: Dict[str, Any] = {}

for classes in plugin_type2class.values():
    for cls in classes:
        name = cls2name[cls]

        plugin_name2cls[name] = cls
        plugin_name2settings[name] = deepcopy(cls.DEFAULTS)

## load plugins

### create storage dir
logger.debug("searching for storage folder")
storage_dir: Path = config_dir / "storage"
if storage_dir.exists() and storage_dir.is_dir():
    logger.info("found storage folder")
else:
    logger.debug("can't find storage folder")
    storage_dir.mkdir(exist_ok=True, parents=True)
    logger.info("created storage folder")

plugin_name2module: Dict[str, Any] = {}

logger.debug("environment: %s", os.environ)
new_settings = get_settings(config=plugin_name2settings)
logger.debug("settings: %s", new_settings)

auth_plugin_name: str = [
    name for name, cls in plugin_name2cls.items() if cls.TYPE == "AUTH"
][0]
logger.debug("loading AUTH plugin with name `%s`", auth_plugin_name)
auth_cls = plugin_name2cls[auth_plugin_name]
if auth_cls.requires_dir:
    auth_module_dir = storage_dir / "auth"
    auth_module_dir.mkdir(exist_ok=True)
else:
    auth_module_dir = None

auth_module = auth_cls(
    new_settings[auth_plugin_name],
    auth_module_dir,
)
plugin_name2module[auth_plugin_name] = auth_module

docs_plugin_name: str = [
    name for name, cls in plugin_name2cls.items() if cls.TYPE == "DOCS"
][0]
logger.debug("loading DOCS plugin with name `%s`", docs_plugin_name)

docs_cls = plugin_name2cls[docs_plugin_name]
if docs_cls.requires_dir:
    docs_module_dir = storage_dir / "docs"
    docs_module_dir.mkdir(exist_ok=True)
else:
    docs_module_dir = None

docs_module = docs_cls(
    new_settings[docs_plugin_name],
    docs_module_dir,
    auth_module if docs_cls.requires_auth else None,
)
plugin_name2module[docs_plugin_name] = docs_module

misc_names = [n for n, c in plugin_name2cls.items() if c.TYPE == "MISC"]
for name in misc_names:
    logger.debug("loading %s MISC plugin", name)
    cls = plugin_name2cls[name]

    if cls.requires_dir:
        module_dir = storage_dir / name
        if not module_dir.exists():
            module_dir.mkdir(exist_ok=True)
    else:
        module_dir = None

    module = cls(
        new_settings[name] if name in new_settings else {},
        module_dir,
        auth_module if cls.requires_auth else None,
        docs_module if cls.requires_docs else None,
    )
    plugin_name2module[name] = module

## add routes
logger.debug("adding CORP policy from auth module")
auth_module.add_CORS(api)

logger.info("adding routes from modules")

token_tester = auth_module.token_tester

for name, module in plugin_name2module.items():
    router = module.create_router(token_tester)

    if module.TYPE in {"AUTH", "DOCS"}:
        api.include_router(router)
    else:
        api.include_router(
            router,
            prefix=f"/{name}",
        )

## setup API
logger.info("setting up API handlers")


@api.on_event("startup")
async def startup_event():
    for name, module in plugin_name2module.items():
        logger.debug("running async_init of module %s", name)
        await module.__async__init__()


@api.get("/info", tags=["root"])
def stats():
    """ basic app info

    Returns
    -------
    str
        basic info
    """
    return {
        "version": __version__,
        "is_uuid_safe": str(uuid.uuid4().is_safe).split(".")[-1],
    }


@api.middleware("http")
async def add_process_time_header(request: Request, call_next: Callable):
    start_time: float = time.time()
    response = await call_next(request)
    process_time: float = time.time() - start_time
    process_time = round(process_time, 2)
    process_time_str: str = str(process_time) + " seconds"
    response.headers["X-Process-Time"] = process_time_str
    return response
