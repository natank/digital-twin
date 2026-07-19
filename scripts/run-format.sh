#!/usr/bin/env bash
# Format Python (Black) and JS/TS (Prettier) across the monorepo.
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

MODE="${1:-write}" # write | check

if [[ "${MODE}" == "check" ]]; then
  echo "==> black --check"
  if command -v poetry >/dev/null 2>&1 && [[ -d apps/backend ]]; then
    (cd apps/backend && poetry run black --check --config ../../pyproject.toml src tests scripts)
    (cd libs/backend-shared && poetry run black --check --config ../../pyproject.toml backend_shared tests)
  else
    black --check --config pyproject.toml apps/backend/src apps/backend/tests apps/backend/scripts \
      libs/backend-shared/backend_shared libs/backend-shared/tests scripts
  fi
  echo "==> prettier --check"
  pnpm exec prettier --check .
else
  echo "==> black"
  if command -v poetry >/dev/null 2>&1 && [[ -d apps/backend ]]; then
    (cd apps/backend && poetry run black --config ../../pyproject.toml src tests scripts)
    (cd libs/backend-shared && poetry run black --config ../../pyproject.toml backend_shared tests)
  else
    black --config pyproject.toml apps/backend/src apps/backend/tests apps/backend/scripts \
      libs/backend-shared/backend_shared libs/backend-shared/tests scripts
  fi
  # Also format root scripts that live outside Poetry packages.
  if [[ -d apps/backend/.venv ]]; then
    apps/backend/.venv/bin/black --config pyproject.toml scripts || true
  fi
  echo "==> prettier --write"
  pnpm exec prettier --write .
fi
