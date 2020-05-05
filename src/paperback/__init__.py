# -*- coding: utf-8 -*-

"""🗄API of 📎PaperText app"""

from .core import App
from .exceptions import TokenException, GeneralException
from .__main__ import get_version

__version__ = get_version()
