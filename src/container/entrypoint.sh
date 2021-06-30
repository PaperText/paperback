#!/usr/bin/env sh

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

for module in $modules; do
    echo "$module"
    pip install "$module"
done

pip install uvloop
pip install argon2-cffi gmpy2

paperback
