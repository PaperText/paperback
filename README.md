PaperBack
=========

[//]: # ([![Documentation Status][docs_badge]][docs_link])
[//]: # (TODO: add container registry link)

[![Checked with mypy][mypy_badge]](http://mypy-lang.org/)
[![Code style: black][black_badge]](https://github.com/psf/black)
[![Imports: isort][isort_badge]](https://pycqa.github.io/isort/)

[![GitLab license][MIT_license_badge]][license_link]

TODO
----
- [ ] add defaults folder with uvicorn config and config folder path

Features
--------
- Uses modern async typed python framework [fastapi](https://fastapi.tiangolo.com/)
- Manages package in `pyproject.toml` with [poetry](https://python-poetry.org/)

[//]: # (- Has a multilayer configuration system, capable of picking up environment variables and config files)
[//]: # (- Implements modular system with 3 types of modules managed by pythons entrypoints)

Usage
-----
1. Install `paperback`
2. Run paperback with `paperback run`
 
[//]: # (1. Install any other module you want.)



Development
-----------
1. get source code
2. run
```shell
docker compose down && docker compose build paperback && docker compose up
```
3. 

Container
---------
Paperback is also available as a container

Contribute
----------
- [Source Code](https://github.com/PaperText/paperback)
- [Issue Tracker](https://github.com/PaperText/paperback/issues)

Support
-------
If you are having issues, please let us know through [issue tracker](https://github.com/PaperText/paperback/issues)

License
-------
The project is licensed under the MIT license.

<!-- links -->
[docs_badge]: https://readthedocs.org/projects/paperback/badge/?version=latest&style=flat-square
[docs_link]: https://paperback.readthedocs.io/en/latest/?badge=latest

[container_badge]: <>
[container_link]: <>

[mypy_badge]: https://img.shields.io/badge/mypy-checked-2a6db2?style=flat-square
[black_badge]: https://img.shields.io/badge/code%20style-black-000000.svg?style=flat-square
[isort_badge]: https://img.shields.io/badge/imports-isort-1674b1?style=flat-square&labelColor=ef8336

[MIT_license_badge]: https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square
[license_link]: https://gitlab.com/PaperText/paperback/blob/master/LICENSE
