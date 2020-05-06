FROM python:3.8-slim AS TRANSLATOR
ARG POETRY_VERSION="1.0.5"
RUN pip install poetry==$POETRY_VERSION
COPY /pyproject.toml /root/pyproject.toml
WORKDIR /root
RUN poetry config cache-dir "/root/poetry_cache"
RUN poetry lock
RUN poetry export --without-hashes -f requirements.txt > requirements.txt
COPY . /root/paperback
WORKDIR /root/paperback
RUN poetry build

FROM python:3.8-slim
RUN apt-get update && \
    apt-get install --no-install-recommends -y build-essential && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
WORKDIR /root
COPY --from=TRANSLATOR /root/requirements.txt /root/requirements.txt
RUN pip install -r requirements.txt
COPY --from=TRANSLATOR /root/paperback/dist /root/dist
RUN pip install /root/dist/paperback*.tar.gz
RUN mkdir /root/.papertext
RUN echo "\
[auth]\n\
    [auth.hash]\n\
        algo = argon2" > /root/.papertext/config.toml
RUN paperback run --debug --create-config
