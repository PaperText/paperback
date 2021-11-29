import os
from pathlib import Path
from typing import Dict, Any, cast
from types import SimpleNamespace

from config import config_from_dict, config_from_env, config_from_toml, ConfigurationSet


def get_settings(
    config_file: Path = None,
    config: Dict[str, Any] = None,
) -> SimpleNamespace:

    if config_file is None:
        config_dir = Path(
            os.environ.get("PT__config_file", Path.home() / ".papertext")
        ).resolve()
        config_file = config_dir / "config.toml"
    if not config_file.exists() and not config_file.is_dir():
        config_file.touch(exist_ok=True)

    if config is None:
        config = {}

    cfg = ConfigurationSet(
        config_from_env(prefix="PT", separator="__"),
        config_from_toml(str(config_file), read_from_file=True),
        config_from_dict(config),
    )
    cfg = cast(SimpleNamespace, cfg)
    return cfg
