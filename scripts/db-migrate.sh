#!/usr/bin/env bash
# Run Alembic migrations to head against the local development database.
#
# Usage:
#   ./scripts/db-migrate.sh
#   ./scripts/db-migrate.sh down     # downgrade one revision
#   ./scripts/db-migrate.sh history  # show migration history

set -euo pipefail

# shellcheck source=scripts/_common.sh
source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/_common.sh"

ensure_env_file
load_env_file

action="${1:-up}"

case "${action}" in
  up|upgrade|head)
    log "Running migrations: upgrade head"
    run_nx run apps/backend:migrate
    ok "Migrations applied (head)"
    ;;
  down|downgrade)
    log "Running migrations: downgrade -1"
    run_nx run apps/backend:migrate-down
    ok "Downgraded one revision"
    ;;
  history)
    log "Migration history"
    run_backend_poetry run alembic history --verbose
    ;;
  current)
    log "Current revision"
    run_backend_poetry run alembic current
    ;;
  -h|--help)
    cat <<'EOF'
Usage: ./scripts/db-migrate.sh [up|down|history|current]

  up (default)  alembic upgrade head  (via nx run apps/backend:migrate)
  down          alembic downgrade -1  (via nx run apps/backend:migrate-down)
  history       alembic history --verbose
  current       alembic current
EOF
    ;;
  *)
    die "Unknown action: ${action} (try --help)"
    ;;
esac
