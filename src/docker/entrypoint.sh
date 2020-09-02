#!/usr/bin/env sh

eval "$(ssh-agent -s)"

chmod 700 ~/.ssh

ssh-keyscan gitlab.com >> ~/.ssh/known_hosts
chmod 644 ~/.ssh/known_hosts

if [ -f file ]; then
    cp ~/.ssh/key ~/.ssh/private_key
    chmod 400 ~/.ssh/private_key
    ssh-add ~/.ssh/private_key
fi

echo "$SSH_PRIVATE_KEY" | tr -d '\r' | ssh-add - > /dev/null


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

paperback -l DEBUG
