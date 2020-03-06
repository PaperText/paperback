from logging import getLogger
from pathlib import Path
from typing import NoReturn

import click
import uvicorn
from fastapi import FastAPI

from . import __version__
from .core import App

default_config_path = Path.home() / ".papertext"
api = FastAPI(
    title="PaperText backend [Paperback]",
    description="BackEnd API for PaperText",
    version=__version__,
)


@click.group()
@click.version_option(version=__version__)
def cli():
    """
    Comand Line Interface for using papertext's backend
    """
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
        click.echo(
            f"config dir: {config}\ncreate_config: {create_config}\ndebug: {debug}"
        )
        click.echo("initializing...", nl=False)
    try:
        app = App(config_path=config, create_config=create_config, verbose=debug)
    except Exception as e:
        if debug:
            raise
        else:
            click.echo(click.style(f"[ {type(e).__name__} ]", fg="red"))
            click.echo(f"\t{e}")
            return
    if debug:
        click.echo("done")
        click.echo("loading local modules...", nl=False)
    app.find_local_modules()

    if debug:
        click.echo("done")
        click.echo("loading pip modules...", nl=False)
    app.find_pip_modules()

    if debug:
        click.echo("done")
        click.echo("loading modules...", nl=False)
    app.load_modules()

    if debug:
        click.echo("done")
        click.echo("adding routers...", nl=False)
    app.add_routers(api)

    if debug:
        click.echo("done")

    @api.get("/")
    def root():
        return {"msg": "Hello, World!"}

    uvicorn.run(
        "paperback.cli:api", host=app.cfg.core.host, port=int(app.cfg.core.port), reload=debug
    )


cli.add_command(run)
