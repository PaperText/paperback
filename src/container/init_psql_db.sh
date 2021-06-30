#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE USER paperback WITH PASSWORD '$paperback_dbuser_passwd';
    CREATE DATABASE auth_module;
    GRANT ALL PRIVILEGES ON DATABASE auth_module, auth_module TO paperback;
EOSQL
