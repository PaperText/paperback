import importlib.util
from pathlib import Path
from sys import modules
from typing import Any, MutableMapping, Union, NoReturn

from config import ConfigurationSet, config_from_dict, config_from_env, config_from_toml
from fastapi import FastAPI
from pkg_resources import iter_entry_points

from .exceptions import DuplicateModuleError, InheritanceError
from .pt_abc import Base, BaseAuth


class App:
    def __init__(self, config_path: Path, create_config: bool, verbose: bool):
        """
        helper function for setting up necessary directory structure
        """
        self.verbose = verbose
        # resolve path to follow symlinks and remove "/../"
        self.config_dir_path = config_path.resolve()
        if self.config_dir_path.exists() and not self.config_dir_path.is_dir():
            raise ValueError(f"given config path ({self.config_dir_path}) isn't a dir")
        if create_config:
            self.config_dir_path.mkdir(parents=True, exist_ok=True)
        elif not self.config_dir_path.exists():
            raise ValueError(
                f"given config path ({self.config_dir_path}) doesn't exist"
            )

        self.config_file_path = self.config_dir_path / "config.toml"
        if create_config:
            self.config_file_path.open("w")
        if not self.config_file_path.exists():
            raise ValueError(
                f"given config path ({self.config_dir_path})"
                " doesn't contain 'config.toml'"
            )

        self.modules_dir_path = self.config_dir_path / "modules"
        if self.modules_dir_path.exists() and not self.modules_dir_path.is_dir():
            raise ValueError(
                f"file {self.modules_dir_path} exists and isn't a directory"
            )
        if create_config:
            self.modules_dir_path.mkdir(parents=True, exist_ok=True)
        elif not self.modules_dir_path.exists():
            raise ValueError(
                f"given config path ({self.config_dir_path})"
                " doesn't contain 'modules' directory"
            )

        self.classes: MutableMapping[str, Any] = {}
        self.modules: MutableMapping[str, Any] = {}
        self.permissions: MutableMapping[str, Any] = {}
        self.default_dict: MutableMapping[str, Any] = {
            "core": {"host": "127.0.0.1", "port": "7878"}
        }

        self.cfg: ConfigurationSet = ConfigurationSet(
            config_from_env(prefix="PT", separator="__"),
            config_from_toml(str(self.config_file_path), read_from_file=True),
            config_from_dict(dict(self.default_dict)),
        )

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
        for entry_point in iter_entry_points("paperback.modules"):
            name = entry_point.name
            cls = entry_point.load()
            if cls.TYPE == "AUTH":
                name = "auth"
            elif cls.TYPE == "TEXTS":
                name = "texts"

            if name in self.classes:
                raise DuplicateModuleError(
                    f'module with name "{name}" already registered'
                )
            else:
                self.classes[name] = cls

    def load_modules(self):
        for name, cls in self.classes.items():
            if not any(issubclass(cls, class_i) for class_i in [Base, BaseAuth]):
                raise InheritanceError(
                    "anu module should ne subclass of Base or BaseAuth"
                )
            self.default_dict[name] = cls.DEFAULTS.copy()
            module = cls(self.cfg[name])
            self.modules[name] = module

    def add_routers(self, api: FastAPI) -> NoReturn:
        for name, module in self.modules.items():
            router = module.create_router()

            if module.TYPE in ["AUTH", "DOCS"]:
                api.include_router(router)
            else:
                api.include_router(
                    router,
                    prefix=f"/{name}",
                )


