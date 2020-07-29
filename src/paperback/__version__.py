from typing import Tuple

__version__: str = "0.2.0"
version_slpitted = __version__.split(".")
if len(version_slpitted) != 3:
    raise ValueError("")
__tuple_version__: Tuple[str, str, str] = (
    version_slpitted[0], version_slpitted[1], version_slpitted[2]
)
