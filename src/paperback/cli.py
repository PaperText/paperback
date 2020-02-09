import sys
from pathlib import Path
from typing import NoReturn

import click

from . import __version__
from .core import App

default_config_path = Path.home() / ".papertext"


@click.group()
@click.version_option(version=__version__)
def cli():
    """
    Comand Line Interface for using papertext's backend
    """
    # click.echo("u used cli")
    pass


@click.command()
@click.option(
    "-c",
    "--config",
    "config",
    default=default_config_path,
    help="path to config folder",
    type=Path,
)
@click.option(
    "--create-config",
    default=False,
    help="flag for creating necessary folders",
    is_flag=True,
)
@click.option("--debug", default=False, help="show debug information", is_flag=True)
def run(config: Path, create_config: bool, debug: bool) -> NoReturn:
    """
    main comand for running API
    """
    if debug:
        click.echo(f"config: {config}\ncreate_config: {create_config}\ndebug: {debug}")
    try:
        app = App(config_path=config, create_config=create_config)
    except Exception as e:
        if debug:
            raise
        else:
            click.echo(click.style(f"[ {type(e).__name__} ]", fg="red"))
            click.echo(f"\t{e}")


cli.add_command(run)
