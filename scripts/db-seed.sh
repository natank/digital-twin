#!/usr/bin/env bash
# Seed the local development database with sample data.
#
# Idempotent — safe to re-run. Uses apps/backend/scripts/seed_data.py via Nx.
#
# Usage:
#   ./scripts/db-seed.sh

set -euo pipefail

# shellcheck source=scripts/_common.sh
source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/_common.sh"

ensure_env_file
load_env_file

log "Seeding development database"
run_nx run apps/backend:seed
ok "Seed complete"
