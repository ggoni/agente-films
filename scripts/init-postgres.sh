#!/bin/bash
set -e

# Create multiple databases if they don't exist
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
    SELECT 'CREATE DATABASE litellm'
    WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'litellm')\gexec
EOSQL

echo "Multiple databases initialized successfully"
