PaperBack
=========
[![GitHub license](https://img.shields.io/github/license/PaperText/paperback?style=flat-square)](https://github.com/PaperText/paperback/blob/master/LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg?style=flat-square)](https://github.com/psf/black)
\
[![Documentation Status](https://readthedocs.org/projects/paperback/badge/?version=latest&style=flat-square)](https://paperback.readthedocs.io/en/latest/?badge=latest)

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

After you're done, push your changes to git.

Container
---------
Paperback is also available as docker-compliant container.

#### Configuration
To configure, pass  variables to docker with `-e`
<table>
    <tr>
        <th>Variable name</th>
        <th>Default value</th>
        <th>Description</th>
    </tr>
    <tr>
        <td>SSH_PRIVATE_KEY</td>
        <td>None, <i><b>required</b></i></td>
        <td>SSH key to use for downloading modules<br>Can be RSA or ecdsa</td>
    </tr>
    <tr>
        <td>MODULES</td>
        <td>"git+https://github.com/PaperText/papertext_auth, git+https://github.com/PaperText/papertext_docs"</td>
        <td>List of pip installable modules</td>
    </tr>
</table> 


You can configure used modules with `MODULES` environment variable.

Example of usage:
1. Basic:
```shell script
podman build . --tag paperback && \
podman run -d \
  -e SSH_PRIVATE_KEY=$SSH_PRIVATE_KEY \
  --network host \
  --name paperback paperback
```
2. Advanced:
This script will mount local folders inside container and install them as modules. This is usefull when you want to develop new module and can't install all dependencies.
```shell script
podman build . --tag paperback && \
podman run -it --rm \
  -v ../papertext_auth:/root/Projects/papertext_auth:z \
  -v ../papertext_docs:/root/Projects/papertext_docs:z \
  -e SSH_PRIVATE_KEY=$SSH_PRIVATE_KEY \
  -e MODULES="[/root/Projects/papertext_auth,/root/Projects/papertext_docs]" \
  --network host \
  --name paperback paperback
```

Contribute
----------
- [Source Code](https://github.com/PaperText/paperback)
- [Issue Tracker](https://github.com/PaperText/paperback/issues)

Support
-------
If you are having issues, please let us know.

License
-------
The project is licensed under the MIT license.
