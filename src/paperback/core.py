from pathlib import Path
from typing import Any, Mapping

from config import ConfigurationSet, config_from_dict, config_from_env, config_from_toml


class App:
    def __init__(self, config_path: Path, create_config: bool):
        """
        helper function for setting up necessary directory structure
        """
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

        self.config_file_path = self.config_dir_path / "config.yaml"
        if create_config:
            self.config_file_path.open("w")
        if not self.config_file_path.exists():
            raise ValueError(
                f"given config path ({self.config_dir_path}) doesn't contain 'config.yaml'"
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
                f"given config path ({self.config_dir_path}) doesn't contain 'modules' directory"
            )
        self.modules: Mapping[str, Any] = {}
        self.default_dict: Mapping[str, Any] = {}

        self.cfg: ConfigurationSet = self.recreate_config()

    def load_modules(self) -> Mapping[str, Any]:
        pass

    def recreate_config(self) -> ConfigurationSet:
        self.cfg = ConfigurationSet(
            config_from_env(prefix="PT_", separator="__"),
            config_from_toml(str(self.config_file_path), read_from_file=True),
            config_from_dict(dict(self.default_dict)),
        )
        return self.cfg
