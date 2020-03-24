from typing import ClassVar

from .base import Base


class BaseText(Base):
    """
    base class for all text modules of PaperText

    Attributes
    ----------
    TYPE: str
        type of module
    DEFAULTS: Dict[str, int]
        python dict of default values for configuration
    """

    TYPE: ClassVar[str] = "TEXTS"

    # def __init__(self, cfg: Mapping[str, Any]):
    # pass
