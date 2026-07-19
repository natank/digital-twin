-- Runs automatically on first container start (mounted into
-- /docker-entrypoint-initdb.d/ by docker-compose.yml).
-- Table creation is owned by Alembic migrations, not this script;
-- this only prepares extensions the migrations rely on.

CREATE EXTENSION IF NOT EXISTS "pgcrypto";
