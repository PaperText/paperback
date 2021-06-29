from pathlib import Path

import click

from . import __version__
from .core import App
from .util import async_lib_name  # noqa

default_config_path = Path.home() / ".papertext"


@click.command()
@click.version_option(version=__version__)
@click.option(
    "-c",
    "--config",
    "config_dir",
    default=default_config_path,
    help="path to config folder",
    type=Path,
)
@click.option(
    "-l",
    "--log",
    "log_level",
    default="INFO",
    help="set logging level",
    envvar="PT__log_level",
    type=click.Choice(
        {"CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", "NOTSET"}
    ),
)
def cli(config_dir: Path, log_level: str):
    """
    main command for running API through CLI
    """
    app = App(config_dir, log_level)
    app.run()


if __name__ == "__main__":
    cli()
