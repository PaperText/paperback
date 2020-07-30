from typing import NoReturn
from pathlib import Path
from subprocess import call

import click

from . import __version__
from .core import App

src_path = Path(__file__) / ".." / ".."
src_path = src_path.resolve()

source_path = src_path / ".."
source_path = source_path.resolve()

pyproject_path = source_path / "pyproject.toml"
pyproject_path = pyproject_path.resolve()


class Scripts:
    @staticmethod
    def lint_flakehell():
        call(f"python -m flakehell lint {src_path}".split(" "))

    @staticmethod
    def lint_mypy():
        call(f"python -m mypy {src_path}".split(" "))

    @staticmethod
    def lint():
        Scripts.lint_flakehell()
        Scripts.lint_mypy()

    @staticmethod
    def fix_black():
        call(
            f"python -m black {src_path} --config {pyproject_path}".split(" ")
        )

    @staticmethod
    def fix_isort():
        call(f"python -m isort -rc {src_path}".split(" "))

    @staticmethod
    def fix():
        Scripts.fix_black()
        Scripts.fix_isort()

    @staticmethod
    def docs_build():
        call(
            f"sphinx-build -b html {src_path / 'paperback_docs'} {source_path / 'docs'}".split(
                " "
            )
        )

    @staticmethod
    def docs_clean():
        call(f"rm -rf {source_path / 'docs'}".split(" "))


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
    type=click.Choice(
        {"CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", "NOTSET"}
    ),
)
def cli(config_dir: Path, log_level: str) -> NoReturn:
    """
    main command for running API through CLI
    """
    app = App(config_dir, log_level)
    app.run()


if __name__ == "__main__":
    cli()
