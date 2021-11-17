#!/bin/bash
set -e

psql --username "$POSTGRES_USER" <<-EOSQL
    CREATE USER $psql_papertext_username WITH PASSWORD '$psql_papertext_password';
    CREATE DATABASE auth_module;
    GRANT ALL PRIVILEGES ON DATABASE auth_module TO $psql_papertext_username;
EOSQL
