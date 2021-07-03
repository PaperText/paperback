FROM python:3.8

EXPOSE 7878

# list of comma separated strings
ENV MODULES="\
    git+https://gitlab.com/papertext/papertext_auth \
    git+https://gitlab.com/PaperText/papertext_docs \
"

ENV PT__auth__hash__algo="argon2"
ENV PT__log_level="INFO"

RUN mkdir ~/.papertext

RUN apt-get update
RUN apt-get install --no-install-recommends -y \
    build-essential \
    libmpc-dev
RUN apt-get clean
RUN rm -rf /var/lib/apt/lists/*

COPY README.md /root/paperback/
COPY LICENSE /root/paperback/
COPY pyproject.toml /root/paperback/
COPY src/paperback /root/paperback/src/paperback
COPY src/container/entrypoint.sh ./entrypoint.sh
COPY src/container/poetry_entrypoint.sh ./poetry_entrypoint.sh

WORKDIR /root/paperback
RUN python3.8 -m pip install --upgrade pip
RUN python3.8 -m pip install --upgrade setuptools
RUN python3.8 -m pip install .

CMD sh ~/entrypoint.sh
