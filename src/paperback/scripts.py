from os import getcwd
from pathlib import Path
from shlex import split
from subprocess import call

cur_path = Path(getcwd()).resolve()

docs_path = cur_path / "docs"
docs_path = docs_path.resolve()

docs_source = cur_path / "src" / "paperback_docs"
docs_source = docs_source.resolve()

docs_dest = cur_path / "docs"
docs_dest = docs_dest.resolve()


class Scripts:
    @staticmethod
    def pretty_print(string):
        print("+-" + "-" * len(string) + "-+")
        print("| " + str(string) + " |")
        print("+-" + "-" * len(string) + "-+")

    @staticmethod
    def execute(cmd):
        return call(split(cmd))

    @staticmethod
    def lint_flake8():
        Scripts.pretty_print("flake8[9] linter")
        Scripts.execute(f"python -m flake8 {cur_path}")

    @staticmethod
    def lint_mypy():
        Scripts.pretty_print("mypy linter")
        Scripts.execute(f"python -m mypy {cur_path}")

    @staticmethod
    def lint():
        Scripts.lint_flake8()
        Scripts.lint_mypy()

    @staticmethod
    def fix_black():
        Scripts.pretty_print("black fixer")
        Scripts.execute(f"python -m black {cur_path}")

    @staticmethod
    def fix_isort():
        Scripts.pretty_print("isort fixer")
        Scripts.execute(f"python -m isort {cur_path}")

    @staticmethod
    def fix():
        Scripts.fix_black()
        Scripts.fix_isort()

    @staticmethod
    def docs_build():
        if docs_source.exists():
            Scripts.execute(f"sphinx-build -b html {docs_source} {docs_dest}")
        else:
            print(f"can't find docs source in {docs_source}")

    @staticmethod
    def docs_clean():
        if docs_dest.exists():
            Scripts.execute(f"rm -rf {docs_dest}")
        else:
            print(f"can't find docs destination in {docs_dest}")
