# -*- coding: utf-8 -*-

"""🗄API of 📎PaperText app"""

__version__ = "0.1.0"

try:
    from .core import App
    from .exceptions import TokenException, GeneralException
#TODO: remove when package will be available at pypi
except ModuleNotFoundError:
    pass
