from typing import NoReturn
from pathlib import Path

import click
import uvicorn
from fastapi import FastAPI

from . import __version__
from .core import App

default_config_path = Path.home() / ".papertext"
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


@click.group()
@click.version_option(version=__version__)
def cli():
    """
    Command Line Interface for using papertext's backend
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
@click.option(
    "--debug", default=False, help="show debug information", is_flag=True
)
def run(config: Path, create_config: bool, debug: bool) -> NoReturn:
    """
    main command for running API
    """
    if debug:
        click.echo(
            f"config dir: {config}\ncreate_config: {create_config}\ndebug: {debug}"
        )
        click.echo("initializing...", nl=False)
    try:
        app = App(
            config_path=config, create_config=create_config, verbose=debug
        )
    except Exception as e:
        if debug:
            raise
        else:
            click.echo(click.style(f"[ {type(e).__name__} ]", fg="red"))
            click.echo(f"\t{e}")
    if debug:
        click.echo("done")
        click.echo(f"config: {app.cfg}")
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
        click.echo("adding handlers...", nl=False)
    app.add_handlers(api)

    if debug:
        click.echo("done")

    uvicorn.run(
        "paperback.cli:api",
        host=app.cfg.core.host,
        port=int(app.cfg.core.port),
    )


cli.add_command(run)
