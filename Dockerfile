FROM python:3.8.5-slim

EXPOSE 7878

# list of comma separated strings
ENV MODULES="\
    git+https://gitlab.com/papertext/papertext_auth \
    git+https://gitlab.com/PaperText/papertext_docs\
"

ENV SSH_PRIVATE_KEY=""

ENV PT__auth__hash__algo="argon2"
ENV PT__log_level="INFO"

RUN mkdir ~/.ssh
RUN mkdir ~/.papertext

RUN apt-get update
RUN apt-get install --no-install-recommends -y \
    build-essential \
    git \
    openssh-client \
    libmpc-dev
RUN apt-get clean
RUN rm -rf /var/lib/apt/lists/*

COPY README.md /root/paperback/
COPY LICENSE /root/paperback/
COPY pyproject.toml /root/paperback/
COPY src/paperback /root/paperback/src/paperback

WORKDIR /root/paperback
RUN pip install "."

COPY src/docker/entrypoint.sh /root/entrypoint.sh
CMD sh ~/entrypoint.sh
