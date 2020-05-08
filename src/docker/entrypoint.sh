#!/usr/bin/env sh

eval $(ssh-agent -s)
echo "$SSH_PRIVATE_KEY" | tr -d '\r' | ssh-add - > /dev/null

mkdir -p ~/.ssh
chmod 700 ~/.ssh
ssh-keyscan github.com >> ~/.ssh/known_hosts
chmod 644 ~/.ssh/known_hosts

mkdir -p ~/.papertext
echo "$CONFIG" > ~/.papertext/config.toml

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
    pip install "$module"
done

paperback run --debug --create-config
