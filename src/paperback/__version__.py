from pathlib import Path

from toml import load

path = Path(__file__).resolve()
while path.name != "src":
    path = path.parent
src_path = path
source_path = src_path / ".."
pyproject_path = source_path / "pyproject.toml"
pyproject_path = pyproject_path.resolve()

pyproject_toml = load(pyproject_path)
__version__ = pyproject_toml["tool"]["poetry"]["version"]
