#!/usr/bin/env sh

# split MODULES env. variable into list of modules
#TODO: maybe change default to list already?

modules=$(python3.8 -c '
import os

modules = os.environ.get("MODULES")
modules = modules.lstrip("[")
modules = modules.rstrip("]")
modules = modules.split(",")

for module in modules:
    module = module.strip()
    print(module)
')

# install modules
for module in $modules; do
    echo "$module"
    poetry install "$module"
done

# install optional dependency of paperback
pip install uvloop

# install optional dependencies of auth module
pip install argon2-cffi gmpy2

# launch paperback
paperback
