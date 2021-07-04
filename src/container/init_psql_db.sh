#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE USER $psql_papertext_username WITH PASSWORD '$psql_papertext_password';
    CREATE DATABASE auth_module;
    GRANT ALL PRIVILEGES ON DATABASE auth_module TO $psql_papertext_username;
EOSQL
