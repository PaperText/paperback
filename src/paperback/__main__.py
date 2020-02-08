# -*- encoding: utf-8 -*-

from pathlib import Path
from subprocess import call

path: Path = Path(__file__) / ".." / ".."
path = path.resolve()


def flake_lint():
    call(f"python -m flakehell lint {path}".split(" "))


def fix_black():
    call(f"python -m black {path}".split(" "))


def fix_isort():
    call(f"python -m isort -rc {path}".split(" "))


def fix_all():
    fix_black()
    fix_isort()
