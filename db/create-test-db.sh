#!/bin/bash
set -e

POSTGRES="psql --username ${POSTGRES_USER}"

echo "Creating test database: ${TEST_DATABASE_NAME}"

$POSTGRES <<EOSQL
CREATE DATABASE ${TEST_DATABASE_NAME} OWNER ${POSTGRES_USER};
EOSQL

echo "Successfully created test database: ${TEST_DATABASE_NAME}"
