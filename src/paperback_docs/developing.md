Developing
==========

Quickstart guide
----------------
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

Maintaining changelog
---------------------
1. tag with a new version
1. change version in  `__version__.py` file
1. push to github with tags, i.e. `git push --tags`

Running in a container
----------------------

### Configuration
To configure, pass  variables to docker with `-e`
<table>
    <tr>
        <th>Variable name</th>
        <th>Default value</th>
        <th>Description</th>
    </tr>
    <tr>
        <td>SSH_PRIVATE_KEY</td>
        <td>"", <i><b>required</b></i></td>
        <td>SSH key to use for downloading modules<br>Can be RSA or ecdsa</td>
    </tr>
    <tr>
        <td>MODULES</td>
        <td>"git+https://github.com/PaperText/papertext_auth, git+https://github.com/PaperText/papertext_docs"</td>
        <td>List of comma separeted, pip installable modules</td>
    </tr>
    <tr>
        <td>CONFIG</td>
        <td><pre>"
[auth]
    [auth.hash]
        algo = "argon2"
"</pre></td>
        <td>Config to use for paperback instance</td>
    </tr>
</table> 

Example of usage with [`podman`](https://podman.io/):
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
  -e CONFIG=$CONFIG \
  --network host \
  --name paperback paperback
```
