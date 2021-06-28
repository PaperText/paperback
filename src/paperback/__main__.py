from pathlib import Path
from subprocess import call
from shlex import split

import click

from . import __version__
from .core import App
from .util import async_lib_name  # noqa

src_path = Path(__file__) / ".." / ".."
src_path = src_path.resolve()

source_path = src_path / ".."
source_path = source_path.resolve()

docs_path = source_path / "docs"
docs_path = docs_path.resolve()

pyproject_path = source_path / "pyproject.toml"
pyproject_path = pyproject_path.resolve()


class Scripts:
    @staticmethod
    def pretty_print(string):
        print("+-"+"-"*len(string)+"-+")
        print("| "+str(string)+" |")
        print("+-" + "-" * len(string) + "-+")

    @staticmethod
    def execute(cmd):
        return call(split(cmd))

    @staticmethod
    def lint_flake8():
        Scripts.pretty_print("flake8[9] linter")
        Scripts.execute(f"python -m flake8 {src_path}")

    @staticmethod
    def lint_mypy():
        Scripts.pretty_print("mypy linter")
        Scripts.execute(f"python -m mypy {src_path}")

    @staticmethod
    def lint():
        Scripts.lint_flake8()
        Scripts.lint_mypy()

    @staticmethod
    def fix_black():
        Scripts.pretty_print("black fixer")
        Scripts.execute(f"python -m black {src_path} --config {pyproject_path}")

    @staticmethod
    def fix_isort():
        Scripts.pretty_print("isort fixer")
        Scripts.execute(f"python -m isort {src_path}")

    @staticmethod
    def fix():
        Scripts.fix_black()
        Scripts.fix_isort()

    @staticmethod
    def docs_build():
        Scripts.execute(f"sphinx-build -b html {src_path / 'paperback_docs'} {docs_path}")

    @staticmethod
    def docs_clean():
        Scripts.execute(f"rm -rf {docs_path}")


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
