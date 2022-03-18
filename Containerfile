ARG BUILD_FROM=docker.io/library/python:3.10-slim
FROM ${BUILD_FROM}

EXPOSE 7878

ENV PYTHONUNBUFFERED=1

LABEL version="0.0"
LABEL description="containerized version of paperback"
LABEL org.opencontainers.image.authors="Danil Kireev <kireev@isa.ru>"

RUN mkdir ~/.papertext
WORKDIR /root/paperback

# install deps
ENV DEBIAN_FRONTEND="noninteractive"

RUN apt-get update && \
    apt-get install --no-install-recommends -y \
        git \
        build-essential \
        libmpc-dev && \
    apt-get clean

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
