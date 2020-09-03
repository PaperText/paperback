import logging
import time
import uuid
from copy import deepcopy
from pathlib import Path
from typing import Any, Callable, Dict, MutableMapping
from collections import defaultdict

import uvicorn
from config import config_from_dict, config_from_env, config_from_toml, ConfigurationSet
from fastapi import FastAPI, Request
from pkg_resources import iter_entry_points
from uvicorn.logging import ColourizedFormatter

from .__version__ import __version__
from .abc import BaseAuth, BaseDocs, BaseMisc
from .exceptions import DuplicateModuleError, InheritanceError
from .util import async_lib_name

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
)


class App:
    def __init__(self, config_path, log_level):
        """
        main class for creating PaperBack instance
        """
        self.config_dir = config_path.resolve()
        self.log_level = log_level

        self.logger = logging.getLogger("paperback")
        self.logger.setLevel(self.log_level)
        tmp_stream_handler = logging.StreamHandler()
        tmp_stream_handler.setLevel("DEBUG")
        self.logger.addHandler(tmp_stream_handler)

        self.logger.debug("setting temporary console-only logger")

        self.logger.debug("checking for logging folder")
        self.logs_dir = self.config_dir / "logs"
        if self.logs_dir.exists() and self.logs_dir.is_dir():
            self.logger.debug("found logging folder")
        else:
            self.logger.debug("can't find logging folder, creating it")
            self.logs_dir.mkdir(parents=True)
            self.logger.debug("created logging folder")

        self.logger.debug("configuring logger")
        self.setup_logging()
        self.logger.handlers = []

        self.logger.info("initializing PaperBack app")

        self.logger.debug("searching for config.toml file")
        self.config_file = self.config_dir / "config.toml"
        if self.config_file.exists() and self.config_file.is_file():
            self.logger.info("found config.toml file")
        else:
            self.logger.debug("can't find config.toml file, creating it")
            self.config_file.touch()
            self.logger.info("created config.toml file")

        self.logger.debug("searching for modules folder")
        self.modules_dir = self.config_dir / "modules"
        if self.modules_dir.exists() and self.modules_dir.is_dir():
            self.logger.info("found modules folder")
        else:
            self.logger.debug("can't find modules folder")
            self.config_file.touch()
            self.logger.info("created modules folder")

        self.logger.debug("searching for storage folder")
        self.storage_dir: Path = self.config_dir / "storage"
        if self.storage_dir.exists() and self.storage_dir.is_dir():
            self.logger.info("found storage folder")
        else:
            self.logger.debug("can't find storage folder")
            self.storage_dir.mkdir(exist_ok=True, parents=True)
            self.logger.info("created storage folder")

        self.default_config: Dict[str, Any] = {
            "core": {"host": "127.0.0.1", "port": "7878",},
        }
        self.classes: MutableMapping[str, Any] = {}
        self.modules: MutableMapping[str, Any] = {}

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

        console_formatter = ColourizedFormatter(
            "{levelprefix:<8} @ {name:<10} : {message}",
            "%Y-%m-%d %H:%M:%S",
            style="{",
            use_colors=True,
        )

        file_handler = logging.handlers.RotatingFileHandler(
            self.logs_dir / "root.log", maxBytes=1024 ** 3, backupCount=20,
        )
        file_handler.setFormatter(text_formatter)
        file_handler.setLevel("DEBUG")
        root_logger.addHandler(file_handler)

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(console_formatter)
        console_handler.setLevel(self.log_level)
        root_logger.addHandler(console_handler)

    def find_local_modules(self):
        pass

    #     for obj in self.modules_dir_path.iterdir():
    #         if obj.name == "__pycache__" and obj.is_dir():
    #             continue
    #         elif obj.is_dir():
    #             name: str = obj.name
    #             location = obj / "__init__.py"
    #             if not location.exists():
    #                 continue
    #         elif obj.suffix == ".py":
    #             name: str = obj.name
    #             if "." in name:
    #                 name = name.split(".")[0]
    #             location = obj
    #         else:
    #             continue
    #         spec = importlib.util.spec_from_file_location(name, location)
    #         module = importlib.util.module_from_spec(spec)
    #         spec.loader.exec_module(module)
    #
    #         self.modules[name] = module
    #         self.default_dict[name] = module.DEFAULTS
    #         self.default_dict[name] = module.DEFAULTS
    #
    #         if self.verbose:
    #             print(f"loaded {module}")

    def find_pip_modules(self):
        self.logger.info("searching for pip modules")
        for entry_point in iter_entry_points("paperback.modules"):
            name = entry_point.name
            cls = entry_point.load()

            if cls.TYPE == "AUTH":
                name = "auth"
            elif cls.TYPE == "DOCS":
                name = "docs"
            self.logger.debug("found %s module", name)

            if not any(
                issubclass(cls, class_i)
                for class_i in [BaseMisc, BaseAuth, BaseDocs]
            ):
                self.logger.error(
                    "module %s doesn't inherit from BaseMisc, BaseAuth or BaseDocs",
                    name,
                )
                raise InheritanceError(
                    "any module should ne subclass of Base or BaseAuth of BaseDocs"
                )

            if name in self.classes:
                self.logger.error("module %s already exists", name)
                raise DuplicateModuleError(
                    f'module with name "{name}" already registered'
                )

            self.classes[name] = cls
            self.default_config[name] = deepcopy(cls.DEFAULTS)

    def load_modules(self):
        self.logger.info("loading modules")
        ddsorter = defaultdict(lambda: 0)
        ddsorter["docs"] = -1
        ddsorter["auth"] = -2
        for name, cls in sorted(
            self.classes.items(),
            key=lambda kv: ddsorter[kv[0]]
        ):
            self.logger.debug("loading %s module", name)
            if cls.requires_dir:
                module_dir = self.storage_dir / name
                if not module_dir.exists():
                    module_dir.mkdir(exist_ok=True)
            else:
                module_dir = None

            if name in {"auth", "docs"}:
                module = cls(
                    self.cfg[name] if name in self.cfg else {}, module_dir,
                )
            else:
                module = cls(
                    self.cfg[name] if name in self.cfg else {},
                    module_dir,
                    self.modules["auth"] if cls.requires_auth else None,
                    self.modules["docs"] if cls.requires_docs else None,
                )
            self.modules[name] = module

    def add_handlers(self, root_api: FastAPI):
        self.logger.info("setting up API handlers")

        @root_api.get("/stats", tags=["root"])
        def stats():
            return {
                "version": __version__,
                "is_uuid_safe": str(uuid.uuid4().is_safe).split(".")[-1],
            }

        @root_api.middleware("http")
        async def add_process_time_header(
            request: Request, call_next: Callable
        ):
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
                    router, prefix=f"/{name}",
                )

    def run(self):
        self.find_pip_modules()
        self.logger.debug("loaded configs: %s", self.cfg)
        self.load_modules()
        self.add_handlers(api)
        self.add_routers(api)

        uvicorn_log_config = uvicorn.config.LOGGING_CONFIG
        del uvicorn_log_config["loggers"]

        self.logger.info("starting uvicorn with %s loop", async_lib_name)
        uvicorn.run(
            "paperback.core:api",
            host=self.cfg.core.host,
            port=int(self.cfg.core.port),
            log_config=uvicorn_log_config,
            log_level=self.log_level.lower(),
            loop=async_lib_name,
            proxy_headers=True,
        )
