from pathlib import Path
from typing import List

import click

from paperback import __version__
from paperback.core import PaperBack
from paperback.util import async_lib_name  # noqa

default_config_path = Path.home() / ".papertext"
CONTEXT_SETTINGS = {
    "help_option_names": ["-h", "--help"],
}


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
@click.pass_context
def cli(ctx: click.Context, config_dir, log_level):
    ctx.ensure_object(dict)

    ctx.obj["get_app"] = lambda: PaperBack(config_dir, log_level)


@cli.command(context_settings=CONTEXT_SETTINGS)
@click.pass_context
def run(ctx: click.Context):
    """
    main command for running API
    """
    ctx.obj["get_app"]().run()


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
    ctx.obj["get_app"]().dev(reload_dirs)
