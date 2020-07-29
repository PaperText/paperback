from pathlib import Path

from toml import load

src_path = Path(__file__) / ".."
source_path = src_path / ".."
pyproject_path = source_path / "pyproject.toml"
pyproject_path = pyproject_path.resolve()

pyproject_toml = load(pyproject_path)
__version__ = pyproject_toml["tool"]["poetry"]["version"]
