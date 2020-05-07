FROM python:3.8-slim

EXPOSE 7878

# list in square brackets OF COMA SEPARATED links
ENV MODULES="\
    git+https://github.com/PaperText/papertext_auth, \
    git+https://github.com/PaperText/papertext_docs\
"

ENV SSH_PRIVATE_KEY=""

RUN apt-get update
RUN apt-get install --no-install-recommends -y build-essential git openssh-server
RUN apt-get clean
RUN rm -rf /var/lib/apt/lists/*

COPY src/paperback /root/paperback/src/paperback
COPY pyproject.toml /root/paperback/
COPY README.md /root/paperback/

WORKDIR /root/paperback
RUN pip install .

WORKDIR /root
COPY src/docker /root
CMD ~/entrypoint.sh
