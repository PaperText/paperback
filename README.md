PaperBack
=========
[![GitHub license](https://img.shields.io/github/license/PaperText/paperback?style=flat-square)](https://github.com/PaperText/paperback/blob/master/LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg?style=flat-square)](https://github.com/psf/black)
\
[![Documentation Status](https://readthedocs.org/projects/paperback/badge/?version=latest&style=flat-square)](https://paperback.readthedocs.io/en/latest/?badge=latest)

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
4. Optionally, configure paperback at `~/.paperback/config.yaml`

Development
-----------
1. install [poetry](https://python-poetry.org/),
    preferably with [pipx](https://pipxproject.github.io/pipx/)
1. download `paperback` from `git` and `cd` into it
1. change `poetry`'s local `virualenvs.path` configuration
    to your preferred virtualenv location with this command:
    `poetry config virtualenvs.path "{your location goes here}" --local`
1. run `poetry install`

You're all set up. Poetry will install dependencies and
    paperback in development mode.

If you want to test your changes you can test them with `paperback run --debug`

After you're done, push your cahnges to git.
