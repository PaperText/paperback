#!/usr/bin/env sh

# install poetry
curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -

# split MODULES env. variable into list of modules
#TODO: maybe change default to list already?

modules=$(python3.8 -c '
import os

modules = os.environ.get("MODULES")
modules = modules.lstrip("[")
modules = modules.rstrip("]")
modules = modules.split(",")

for module in modules:
    print(module.strip())
')

# install modules
for module in $modules; do
    echo "$module"
    poetry install --no-dev "$module"
done


# still need to install optional dependency of paperback
pip install uvloop

# from default entrypoint
# should be instralled as optional dependencies by poetry
# pip install argon2-cffi gmpy2


# launch paperback
paperback
