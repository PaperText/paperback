# -*- encoding: utf-8 -*-

from pathlib import Path
from subprocess import call

path = Path(__file__) / ".." / ".."
path = path.resolve()

source_path = path / ".."
source_path = source_path.resolve()

pyproject_path = source_path / "pyproject.toml"
pyproject_path = pyproject_path.resolve()


def flake_lint():
    call(f"python -m flakehell lint {path}".split(" "))


def fix_black():
    call(f"python -m black {path} --config {pyproject_path}".split(" "))


def fix_isort():
    call(f"python -m isort -rc {source_path}".split(" "))


def fix_all():
    fix_black()
    fix_isort()

def build_docs():
    call(f"sphinx-build -b html {source_path/'docs'} {source_path/'docs_out'}".split(" "))

if __name__ == "__main__":
    call("paperback run --debug".split(" "))
