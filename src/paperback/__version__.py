from pathlib import Path
from typing import Optional, Dict

from toml import load

path: Path = (Path(__file__)/"..").resolve()
pyproject_path: Optional[Path] = None

while not pyproject_path:
    for child in path.iterdir():
        if child.name == "pyproject.toml":
            pyproject_path = child
    path = path.parent

pyproject_toml: Dict = load(pyproject_path)
__version__ = pyproject_toml["tool"]["poetry"]["version"]
