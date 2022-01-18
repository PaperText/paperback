FROM docker.io/library/python:3.10-slim

EXPOSE 7878

LABEL version="0.0"
LABEL description="development version of paperback \
doesn't build the app, only installs dependencies"
LABEL org.opencontainers.image.authors="Danil Kireev <kireev@isa.ru>"

# install deps
ENV DEBIAN_FRONTEND="noninteractive"
RUN apt update && \
    apt install --no-install-recommends -y \
        git \
        build-essential \
        libmpc-dev && \
    apt clean

# upgrade pip and setuptools
RUN python -m pip install --upgrade pip setuptools

# install poetry
RUN pip install poetry
ENV PATH /root/.local/bin:$PATH

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

COPY pyproject.toml             ./
COPY poetry.lock                ./
COPY ./src/paperback/scripts.py ./src/paperback/
COPY LICENSE                    ./
COPY README.md                  ./

RUN poetry config --local virtualenvs.create false
RUN poetry install

# COPY ./src/paperback/                ./src/paperback/
COPY ./src/container/install_deps.sh ./src/container/install_deps.sh

RUN ./src/container/install_deps.sh

CMD uvicorn --host 0.0.0.0 --port 7878 --log-level info --use-colors paperback.app:app
