from pathlib import Path
from subprocess import call


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
        f"sphinx-build -b html {src_path / 'papertext_docs'} {source_path / 'docs'}".split(
            " "
        )
    )

def get_version():
    import yaml

    pyproject = yaml.load(pyproject_path)
    version = pyproject["tool"]["poetry"]["version"]

    return version

if __name__ == "__main__":
    from .cli import cli
    cli()
