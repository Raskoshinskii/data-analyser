#!/bin/bash

set -e
set -u

function create_database() {
  local database=$1
  echo "Creating database '$database'"
  psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
    CREATE DATABASE $database;
    GRANT ALL PRIVILEGES ON DATABASE $database TO $POSTGRES_USER;
    ALTER DATABASE $database OWNER TO $POSTGRES_USER;
    \c $database
    CREATE SCHEMA IF NOT EXISTS public;
    GRANT ALL PRIVILEGES ON SCHEMA public TO $POSTGRES_USER;
    ALTER SCHEMA public OWNER TO $POSTGRES_USER;
EOSQL
  echo "Database '$database' created and permissions granted"
}

if [ -n "$POSTGRES_MULTIPLE_DATABASES" ]; then
  echo "Multiple database creation requested: $POSTGRES_MULTIPLE_DATABASES"
  for db in $(echo $POSTGRES_MULTIPLE_DATABASES | tr ',' ' '); do
    if [ "$db" != "$POSTGRES_DB" ]; then
      create_database $db
    fi
  done
  echo "Multiple databases created"
fi
