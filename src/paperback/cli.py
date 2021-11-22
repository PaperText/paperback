import os
from pathlib import Path
from typing import List

import click
import uvicorn

from paperback import __version__
from paperback.util import get_async_lib_name  # noqa

default_config_path = Path.home() / ".papertext"
default_config_path = default_config_path.resolve()

CONTEXT_SETTINGS = {
    "help_option_names": ["-h", "--help"],
}

uvicorn_log_config = uvicorn.config.LOGGING_CONFIG
# del uvicorn_log_config["loggers"]

@click.group(context_settings=CONTEXT_SETTINGS)
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
    type=click.Choice({"CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", "NOTSET"}),
)
@click.option(
    "-h",
    "--host",
    "host",
    envvar="PT__host",
    help="specify host for server to listen on",
    type=str,
    default="0.0.0.0",
)
@click.option(
    "-p",
    "--port",
    "port",
    envvar="PT__port",
    help="specify port for server to listen on",
    type=int,
    default=7878,
)
@click.pass_context
def cli(ctx: click.Context, config_dir: Path, log_level: str, host: str, port: int):
    ctx.ensure_object(dict)

    os.environ["PT__config_dir"] = str(config_dir)
    os.environ["PT__log_level"] = str(log_level)

    ctx.obj["host"] = str(host)
    ctx.obj["port"] = int(port)
    ctx.obj["log_level"] = str(log_level)


@cli.command(context_settings=CONTEXT_SETTINGS)
@click.pass_context
def run(ctx: click.Context):
    """
    main command for running API
    """
    uvicorn.run(
        "paperback.app:api",
        host=ctx.obj["host"],
        port=ctx.obj["port"],
        log_config=uvicorn_log_config,
        log_level=ctx.obj["log_level"].lower(),
        loop=get_async_lib_name(),
        proxy_headers=True,
        use_colors=True,
    )


@cli.command(context_settings=CONTEXT_SETTINGS)
@click.option(
    "-r",
    "--reload-dirs",
    "reload_dirs",
    default=["/root/paperback/src/paperback"],
    help="path to folder to watch for changes",
    type=Path,
    multiple=True,
)
@click.pass_context
def dev(ctx: click.Context, reload_dirs: List[Path]):
    """
    command for running API in development mode
    """
    uvicorn.run(
        "paperback.app:api",
        host=ctx.obj["host"],
        port=ctx.obj["port"],
        log_config=uvicorn_log_config,
        log_level=ctx.obj["log_level"].lower(),
        loop=get_async_lib_name(),
        proxy_headers=True,
        reload=True,
        reload_dirs=reload_dirs,
        use_colors=True,
    )
