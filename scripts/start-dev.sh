#!/usr/bin/env bash
# Start the local development infrastructure stack.
#
# 1. Ensures .env.local exists
# 2. Validates environment variables
# 3. Starts docker compose (Postgres, Redis, LocalStack)
# 4. Waits for services to be ready
# 5. Runs database migrations
# 6. Prints next-step instructions (app servers are started separately)
#
# Usage:
#   ./scripts/start-dev.sh
#   ./scripts/start-dev.sh --seed          # also seed sample data
#   ./scripts/start-dev.sh --no-migrate    # skip migrations
#   ./scripts/start-dev.sh --skip-validate # skip env validation

set -euo pipefail

# shellcheck source=scripts/_common.sh
source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/_common.sh"

DO_MIGRATE=1
DO_SEED=0
DO_VALIDATE=1

usage() {
  cat <<'EOF'
Usage: ./scripts/start-dev.sh [options]

Options:
  --seed            Run database seed after migrations
  --no-migrate      Skip alembic migrations
  --skip-validate   Skip environment variable validation
  -h, --help        Show this help
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --seed) DO_SEED=1; shift ;;
    --no-migrate) DO_MIGRATE=0; shift ;;
    --skip-validate) DO_VALIDATE=0; shift ;;
    -h|--help) usage; exit 0 ;;
    *) die "Unknown option: $1 (try --help)" ;;
  esac
done

log "Digital Twin — starting local development environment"
log "Repo root: ${ROOT_DIR}"

ensure_env_file
load_env_file

if [[ "${DO_VALIDATE}" -eq 1 ]]; then
  log "Validating environment"
  python3 "${ROOT_DIR}/scripts/validate-env.py" --env-file "${ENV_FILE}" \
    || die "Environment validation failed"
fi

require_compose
log "Starting docker compose services"
compose up -d
ok "compose up -d completed"

wait_for_compose_healthy 90

# LocalStack is optional for pure DB work but expected for S3 simulation.
if (echo >/dev/tcp/127.0.0.1/4566) >/dev/null 2>&1; then
  ok "LocalStack is reachable on :4566"
else
  warn "LocalStack not yet reachable on :4566 (S3 simulation may be unavailable)"
fi

if [[ "${DO_MIGRATE}" -eq 1 ]]; then
  log "Running database migrations"
  run_nx run apps/backend:migrate
  ok "Migrations applied"
fi

if [[ "${DO_SEED}" -eq 1 ]]; then
  log "Seeding database"
  run_nx run apps/backend:seed
  ok "Seed complete"
fi

# Soft service check (reports but does not fail the script after infra is up).
python3 "${ROOT_DIR}/scripts/validate-env.py" \
  --env-file "${ENV_FILE}" \
  --check-services \
  || warn "Service reachability check reported issues (see above)"

cat <<EOF

----------------------------------------------------------
 Local development stack is ready

   PostgreSQL  localhost:5432  (db: digital_twin_dev)
   Redis       localhost:6379
   LocalStack  localhost:4566  (S3)

 Next steps — start application servers in separate terminals:

   pnpm nx serve apps/backend     # API  http://localhost:8000
   pnpm nx serve apps/frontend    # UI   http://localhost:4200

 Useful commands:

   ./scripts/db-migrate.sh
   ./scripts/db-seed.sh
   ./scripts/db-reset.sh
   python3 scripts/validate-env.py --check-services

 API docs (once backend is running): http://localhost:8000/docs
----------------------------------------------------------
EOF
