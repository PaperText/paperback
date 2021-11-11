import logging
import time
import uuid
from collections import defaultdict
from copy import deepcopy
from pathlib import Path
from typing import Any, Callable, Dict, List, MutableMapping

import uvicorn
from config import config_from_dict, config_from_env, config_from_toml, ConfigurationSet
from fastapi import FastAPI, Request
from pkg_resources import iter_entry_points
from uvicorn.logging import ColourizedFormatter

from paperback import __version__
from paperback.abc import BaseAuth, BaseDocs, BaseMisc
from paperback.app import api
from paperback.exceptions import DuplicateModuleError, InheritanceError
from paperback.std import AuthImplemented, DocsImplemented
from paperback.util import async_lib_name


class App:
    def __init__(self, config_path, log_level):
        """
        main class for creating PaperBack instance
        """
        self.config_dir = config_path.resolve()
        self.log_level = log_level

        # set up basic logger
        self.logger = logging.getLogger("paperback")
        self.logger.setLevel(self.log_level)
        tmp_stream_handler = logging.StreamHandler()
        tmp_stream_handler.setLevel("DEBUG")
        self.logger.addHandler(tmp_stream_handler)
        self.logger.debug("temporary console-only logger was set up")

        self.logger.debug("checking for logging folder")
        self.logs_dir = self.config_dir / "logs"
        if self.logs_dir.exists() and self.logs_dir.is_dir():
            self.logger.debug("found logging folder")
        else:
            self.logger.debug("can't find logging folder, creating it")
            self.logs_dir.mkdir(parents=True)
            self.logger.debug("created logging folder")

        self.logger.debug("configuring logger")
        self.logger.removeHandler(tmp_stream_handler)
        self.setup_logging()
        self.logger.info("initializing PaperBack app")

        self.api = api

        self.logger.debug("searching for config.toml file")
        self.config_file = self.config_dir / "config.toml"
        if self.config_file.exists() and self.config_file.is_file():
            self.logger.info("found config.toml file")
        else:
            self.logger.debug("can't find config.toml file, creating it")
            self.config_file.touch()
            self.logger.info("created config.toml file")

        self.logger.debug("searching for storage folder")
        self.storage_dir: Path = self.config_dir / "storage"
        if self.storage_dir.exists() and self.storage_dir.is_dir():
            self.logger.info("found storage folder")
        else:
            self.logger.debug("can't find storage folder")
            self.storage_dir.mkdir(exist_ok=True, parents=True)
            self.logger.info("created storage folder")

        self.default_config: Dict[str, Any] = {
            "core": {
                "host": "127.0.0.1",
                "port": "7878",
            },
        }
        self.classes: MutableMapping[str, Any] = {}
        self.modules: MutableMapping[str, Any] = {}
        self.to_run_async: List[Callable] = []

    @property
    def cfg(self) -> ConfigurationSet:
        cfg = ConfigurationSet(
            config_from_env(prefix="PT", separator="__"),
            config_from_toml(self.config_file, read_from_file=True),
            config_from_dict(self.default_config),
        )
        return cfg

    def setup_logging(self):
        root_logger = logging.getLogger()

        text_formatter = logging.Formatter(
            "{levelname:<8} in {name:<16} at {asctime:<16}: {message}",
            "%Y-%m-%d %H:%M:%S",
            style="{",
        )

        file_handler = logging.handlers.RotatingFileHandler(
            self.logs_dir / "root.log",
            maxBytes=1024 ** 3,
            backupCount=20,
        )
        file_handler.setFormatter(text_formatter)
        file_handler.setLevel("DEBUG")
        root_logger.addHandler(file_handler)

        console_formatter = ColourizedFormatter(
            "{levelprefix:<8} @ {name:<10} : {message}",
            "%Y-%m-%d %H:%M:%S",
            style="{",
            use_colors=True,
        )

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(console_formatter)
        console_handler.setLevel(self.log_level)
        root_logger.addHandler(console_handler)

    def find_pip_modules(self):
        self.logger.info("searching for pip modules")

        for name, cls in {"auth": AuthImplemented, "docs": DocsImplemented}.items():
            self.classes[name] = cls
            self.default_config[name] = deepcopy(cls.DEFAULTS)

        for entry_point in iter_entry_points("paperback.modules"):
            name = entry_point.name
            cls = entry_point.load()

            if cls.TYPE == "AUTH":
                name = "auth"
            elif cls.TYPE == "DOCS":
                name = "docs"
            self.logger.debug("found %s module", name)

            if not any(
                issubclass(cls, class_i) for class_i in [BaseMisc, BaseAuth, BaseDocs]
            ):
                self.logger.error(
                    "module %s doesn't inherit from BaseMisc, BaseAuth or BaseDocs",
                    name,
                )
                raise InheritanceError(
                    f"module {name} doesn't inherit from BaseMisc, BaseAuth or BaseDocs"
                )

            if name in self.classes:
                self.logger.error("module %s already exists", name)
                raise DuplicateModuleError(
                    f'module with name "{name}" already registered'
                )

            self.classes[name] = cls
            self.default_config[name] = deepcopy(cls.DEFAULTS)

    # rewrite to get better errors and better manage auth and docs modules
    def load_modules(self):
        self.logger.info("loading modules")

        auth_module_dir = self.storage_dir / "auth"
        auth_module_dir.mkdir(exist_ok=True)
        self.modules["auth"] = AuthImplemented(
            self.cfg["auth"],
            auth_module_dir,
        )
        self.to_run_async.append(AuthImplemented.__async__init__)

        docs_module_dir = self.storage_dir / "docs"
        docs_module_dir.mkdir(exist_ok=True)
        self.modules["docs"] = DocsImplemented(
            self.cfg["docs"] if "docs" in self.cfg else {},
            docs_module_dir,
            self.modules["auth"],
        )
        self.to_run_async.append(DocsImplemented.__async__init__)

        for name, cls in self.classes.items():
            self.logger.debug("loading %s module", name)

            if cls.requires_dir:
                module_dir = self.storage_dir / name
                if not module_dir.exists():
                    module_dir.mkdir(exist_ok=True)
            else:
                module_dir = None

            if name == "auth":
                module = cls(self.cfg[name] if name in self.cfg else {}, module_dir)
            elif name == "docs":
                module = cls(
                    self.cfg[name] if name in self.cfg else {},
                    module_dir if cls.requires_dir else None,
                    self.modules["auth"] if cls.requires_auth else None,
                )
            else:
                module = cls(
                    self.cfg[name] if name in self.cfg else {},
                    module_dir if cls.requires_dir else None,
                    self.modules["auth"] if cls.requires_auth else None,
                    self.modules["docs"] if cls.requires_docs else None,
                )

            self.modules[name] = module

            self.to_run_async.append(module.__async__init__)

    def add_handlers(self, root_api: FastAPI):
        self.logger.info("setting up API handlers")

        @root_api.on_event("startup")
        async def startup_event():
            for event in self.to_run_async:
                await event()

        @root_api.get("/stats", tags=["root"])
        def stats():
            return {
                "version": __version__,
                "is_uuid_safe": str(uuid.uuid4().is_safe).split(".")[-1],
            }

        @root_api.middleware("http")
        async def add_process_time_header(request: Request, call_next: Callable):
            start_time: float = time.time()
            response = await call_next(request)
            process_time: float = time.time() - start_time
            process_time = round(process_time, 2)
            process_time_str: str = str(process_time) + " seconds"
            response.headers["X-Process-Time"] = process_time_str
            return response

        self.logger.debug("adding CORP policy from auth module")
        self.modules["auth"].add_CORS(root_api)

    def add_routers(self, root_api: FastAPI):
        self.logger.info("adding routes from modules")

        token_tester = self.modules["auth"].token_tester

        for name, module in self.modules.items():
            router = module.create_router(token_tester)

            if module.TYPE in ["AUTH", "DOCS"]:
                root_api.include_router(router)
            else:
                root_api.include_router(
                    router,
                    prefix=f"/{name}",
                )

    def setup(self):
        self.find_pip_modules()
        self.logger.debug("loaded configs: %s", self.cfg)
        self.load_modules()
        self.add_handlers(self.api)
        self.add_routers(self.api)

    def run(self):
        self.setup()

        uvicorn_log_config = uvicorn.config.LOGGING_CONFIG
        del uvicorn_log_config["loggers"]

        self.logger.info("starting uvicorn with %s loop", async_lib_name)
        uvicorn.run(
            "paperback.app:api",
            host=self.cfg.core.host,
            port=int(self.cfg.core.port),
            log_config=uvicorn_log_config,
            log_level=self.log_level.lower(),
            loop=async_lib_name,
            proxy_headers=True,
        )

    def dev(self):
        self.setup()

        uvicorn_log_config = uvicorn.config.LOGGING_CONFIG
        del uvicorn_log_config["loggers"]

        self.logger.info(
            "starting uvicorn in development mode with %s loop", async_lib_name
        )
        uvicorn.run(
            "paperback.app:api",
            host=self.cfg.core.host,
            port=int(self.cfg.core.port),
            log_config=uvicorn_log_config,
            log_level=self.log_level.lower(),
            loop=async_lib_name,
            proxy_headers=True,
            reload=True,
        )
