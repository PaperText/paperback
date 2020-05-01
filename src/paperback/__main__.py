from pathlib import Path
from subprocess import call

from .cli import cli

src_path = Path(__file__) / ".." / ".."
src_path = src_path.resolve()

source_path = src_path / ".."
source_path = source_path.resolve()

pyproject_path = source_path / "pyproject.toml"
pyproject_path = pyproject_path.resolve()

def lint():
    call(f"python -m flakehell lint {src_path}".split(" "))


def fix_black():
    call(f"python -m black {src_path} --config {pyproject_path}".split(" "))


def fix_isort():
    call(f"python -m isort -rc {src_path}".split(" "))


def fix():
    fix_black()
    fix_isort()


def docs():
    call(
        f"sphinx-build -b html {source_path / 'docs'} {source_path / 'docs_out'}".split(
            " "
        )
    )


if __name__ == "__main__":
    cli()
