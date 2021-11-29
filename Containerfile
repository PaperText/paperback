FROM python:3.8

# install deps
RUN apt-get update
RUN apt-get install --no-install-recommends -y \
    build-essential \
    libmpc-dev
RUN apt-get clean
RUN rm -rf /var/lib/apt/lists/*

# upgrade pip and setuptools
RUN python3.8 -m pip install --upgrade pip setuptools

# install optional dependency of paperback
RUN pip install orjson --no-cache-dir

# install optional dependencies of auth module
RUN pip install argon2-cffi gmpy2 --no-cache-dir

# set changeable variables
EXPOSE 7878

# list of comma separated strings
ENV MODULES=""

ENV PT__auth__hash__algo="argon2"
ENV PT__log_level="INFO"

# changeable stuff

RUN mkdir ~/.papertext

WORKDIR /root/paperback

COPY README.md                       ./
COPY LICENSE                         ./
COPY pyproject.toml                  ./
COPY ./src/paperback                 ./src/paperback
COPY ./src/container/install_deps.sh ./install_deps.sh

RUN python3.8 -m pip install .
RUN ./install_deps.sh

CMD paperback run
