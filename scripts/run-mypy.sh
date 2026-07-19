#!/usr/bin/env bash
# Type-check Python packages with the project Poetry environments.
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

status=0

echo "==> mypy libs/backend-shared"
(
  cd libs/backend-shared
  poetry run mypy backend_shared --config-file ../../mypy.ini
) || status=1

echo "==> mypy apps/backend"
(
  cd apps/backend
  # Package layout is the flat `src/` package (Poetry package name digital-twin-backend).
  poetry run mypy src --config-file ../../mypy.ini
) || status=1

echo "==> mypy scripts/validate-env.py"
(
  # Use backend venv if available (has pytest/deps); fall back to poetry run.
  if [[ -x apps/backend/.venv/bin/mypy ]]; then
    apps/backend/.venv/bin/mypy scripts/validate-env.py --config-file mypy.ini
  else
    cd apps/backend && poetry run mypy ../../scripts/validate-env.py --config-file ../../mypy.ini
  fi
) || status=1

exit "${status}"
