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
    print(module.strip())
')

# install modules
for module in $modules; do
    echo "$module"
    pip install "$module"
done
