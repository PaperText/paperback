PaperBack
=========
[![Documentation Status](https://readthedocs.org/projects/paperback/badge/?version=latest&style=flat-square)](https://paperback.readthedocs.io/en/latest/?badge=latest)
[![Docker Repository on Quay](https://quay.io/repository/randomunrandom/paperback/status?style=flat-square)](https://quay.io/repository/randomunrandom/paperback)
\
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg?style=flat-square)](https://github.com/psf/black)
[![GitHub license](https://img.shields.io/github/license/PaperText/paperback?style=flat-square)](https://github.com/PaperText/paperback/blob/master/LICENSE)

Features
--------
- Uses modern async typed python framework [fastapi](https://fastapi.tiangolo.com/)
- Manages package in `pyproject.toml` with [poetry](https://python-poetry.org/)
- Implements module system with 3 types of modules 
    managed by python's package manager `pip`
- Has a multilayer configuration system,
    capable of picking up environment variables with separators

Usage
-----
1. Install `paperback` with any `auth` and `docs` modules.
    You can use standard implementation, 
    i.e. [`papertext_auth`]() and [`papertext_docs`]().
2. Install any miscellaneous modules you want.
3. Run paperback with `paperback run --create-config`\
Note 📓:\
    You don't need to always run paperback with `--create-config` flag.
    After first startup you can just use `paperback run`.
4. Optionally, configure paperback at `~/.paperback/config.toml`

Container
---------
Paperback is also available as docker-compliant container.
You can read more in [docs]()

Contribute
----------
- [Source Code](https://github.com/PaperText/paperback)
- [Issue Tracker](https://github.com/PaperText/paperback/issues)

Support
-------
If you are having issues, please let us know through
[issue tracker](https://github.com/PaperText/paperback/issues).

License
-------
The project is licensed under the MIT license.
