from pathlib import Path

from toml import load

path = Path(__file__).resolve()
while path.name != "paperback":
    path = path.parent
source_path = path
pyproject_path = source_path / "pyproject.toml"
pyproject_path = pyproject_path.resolve()

pyproject_toml = load(pyproject_path)
__version__ = pyproject_toml["tool"]["poetry"]["version"]
