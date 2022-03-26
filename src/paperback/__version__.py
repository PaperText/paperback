from importlib.metadata import version
from typing import Tuple

__version__ = version("paperback")
version_split = __version__.split(".")
__tuple_version__ = (
    version_split[0],
    version_split[1],
    version_split[2],
)
