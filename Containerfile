FROM docker.io/library/python:3.8-slim

EXPOSE 7878

ENV PYTHONDONTWRITEBYTECODE=1

# install deps
ENV DEBIAN_FRONTEND="noninteractive"
RUN apt update && \
    apt install --no-install-recommends -y \
        git \
        build-essential \
        libmpc-dev && \
    apt clean

# upgrade pip and setuptools
RUN python3.8 -m pip install --upgrade pip setuptools

## install optional dependency of paperback
RUN pip install --no-cache-dir orjson

## install optional dependencies of auth module
RUN pip install --no-cache-dir argon2-cffi gmpy2

# changeable stuff

## list of comma separated strings
ENV MODULES=""

#
ENV PT__auth__hash__algo="argon2"
ENV PT__log_level="INFO"

RUN mkdir ~/.papertext

WORKDIR /root/paperback

COPY LICENSE                         ./
COPY README.md                       ./
COPY pyproject.toml                  ./
COPY ./src/paperback                 ./src/paperback
COPY ./src/container/install_deps.sh ./install_deps.sh

RUN python3.8 -m pip install .
RUN ./install_deps.sh

CMD paperback run
