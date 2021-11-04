PaperBack
=========
[![Documentation Status][docs_badge]][docs_link]
[![Docker Repository on Quay][container_badge]][container_link]

[![Checked with mypy][mypy_badge]](http://mypy-lang.org/)
[![Code style: black][black_badge]](https://github.com/psf/black)
[![Imports: isort][isort_badge]](https://pycqa.github.io/isort/)

[![GitLab license][MIT_license_badge]][license_link]

Features
--------
- Uses modern async typed python framework [fastapi](https://fastapi.tiangolo.com/)
- Manages package in `pyproject.toml` with [poetry](https://python-poetry.org/)
- Implements modular system with 3 types of modules managed by pythons entrypoints
- Has a multilayer configuration system, capable of picking up environment variables and config files

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

<!-- links -->
[docs_badge]: https://readthedocs.org/projects/paperback/badge/?version=latest&style=flat-square
[docs_link]: https://paperback.readthedocs.io/en/latest/?badge=latest

[container_badge]: https://quay.io/repository/papertext/paperback/status?style=flat-square
[container_link]: https://quay.io/repository/papertext/paperback

[mypy_badge]: https://img.shields.io/badge/mypy-checked-2a6db2?style=flat-square
[black_badge]: https://img.shields.io/badge/code%20style-black-000000.svg?style=flat-square
[isort_badge]: https://img.shields.io/badge/imports-isort-1674b1?style=flat-square&labelColor=ef8336

[MIT_license_badge]: https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square
[license_link]: https://gitlab.com/PaperText/paperback/blob/master/LICENSE
