# -*- encoding: utf-8 -*-

from pathlib import Path
from subprocess import call

from . import cli

path: Path = Path(__file__) / ".." / ".."
path = path.resolve()

src_path: Path = path / ".."
src_path = path.resolve()

pyproject_path = path / ".." / "pyproject.toml"
pyproject_path = pyproject_path.resolve()


def flake_lint():
    call(f"python -m flakehell lint {path}".split(" "))


def fix_black():
    call(f"python -m black {path} --config {pyproject_path}".split(" "))


def fix_isort():
    call(f"python -m isort -rc {src_path}".split(" "))


def fix_all():
    fix_black()
    fix_isort()


if __name__ == "__main__":
    cli()
