#!/usr/bin/env bash
# Reset the local development database to a clean slate.
#
# Drops the Postgres data volume, restarts the postgres service, re-runs
# migrations, and (by default) re-seeds sample data.
#
# WARNING: This destroys all local Postgres data for this project.
#
# Usage:
#   ./scripts/db-reset.sh
#   ./scripts/db-reset.sh --no-seed
#   ./scripts/db-reset.sh --yes          # skip confirmation prompt

set -euo pipefail

# shellcheck source=scripts/_common.sh
source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/_common.sh"

DO_SEED=1
ASSUME_YES=0

usage() {
  cat <<'EOF'
Usage: ./scripts/db-reset.sh [options]

Options:
  --no-seed   Do not run the seed script after migrations
  --yes, -y   Skip the confirmation prompt
  -h, --help  Show this help
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --no-seed) DO_SEED=0; shift ;;
    --yes|-y) ASSUME_YES=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) die "Unknown option: $1 (try --help)" ;;
  esac
done

ensure_env_file
load_env_file
require_compose

if [[ "${ASSUME_YES}" -ne 1 ]]; then
  cat <<'EOF'
WARNING: This will destroy all local PostgreSQL data for digital-twin
(volume: postgres_data), re-run migrations, and optionally re-seed.
EOF
  read -r -p "Type 'reset' to continue: " confirm
  if [[ "${confirm}" != "reset" ]]; then
    die "Aborted (expected 'reset', got '${confirm}')"
  fi
fi

log "Stopping compose stack and removing postgres data volume"
# Stop all services first so the volume is not in use.
compose down

# Remove the named postgres volume. Compose project name defaults to the
# directory name ("digital-twin"); try common volume name patterns.
volume_removed=0
for vol in \
  "digital-twin_postgres_data" \
  "digitaltwin_postgres_data" \
  "$(basename "${ROOT_DIR}")_postgres_data"
do
  if docker volume inspect "${vol}" >/dev/null 2>&1; then
    docker volume rm "${vol}"
    ok "Removed volume ${vol}"
    volume_removed=1
  fi
done

if [[ "${volume_removed}" -eq 0 ]]; then
  # Fallback: let compose remove anonymous/project volumes tied to the stack.
  warn "Named postgres volume not found by common names; using 'compose down -v'"
  compose down -v || true
fi

log "Starting compose stack fresh"
compose up -d
wait_for_compose_healthy 90

log "Running migrations on empty database"
run_nx run apps/backend:migrate
ok "Migrations applied"

if [[ "${DO_SEED}" -eq 1 ]]; then
  log "Seeding database"
  run_nx run apps/backend:seed
  ok "Seed complete"
fi

cat <<'EOF'

----------------------------------------------------------
 Database reset complete.

   ./scripts/db-migrate.sh   # re-run migrations later
   ./scripts/db-seed.sh      # re-seed without full reset
----------------------------------------------------------
EOF
