#!/usr/bin/env bash
# Shared helpers for digital-twin development scripts.
# shellcheck shell=bash

# Resolve monorepo root from this file's location (scripts/_common.sh).
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

ENV_FILE="${ROOT_DIR}/.env.local"
ENV_EXAMPLE="${ROOT_DIR}/.env.example"
COMPOSE_FILE="${ROOT_DIR}/docker-compose.yml"

# Prefer docker compose v2 plugin; fall back to docker-compose / podman-compose.
if docker compose version >/dev/null 2>&1; then
  COMPOSE=(docker compose)
elif command -v docker-compose >/dev/null 2>&1; then
  COMPOSE=(docker-compose)
elif command -v podman-compose >/dev/null 2>&1; then
  COMPOSE=(podman-compose)
else
  COMPOSE=()
fi

log()  { printf '==> %s\n' "$*"; }
ok()   { printf '    OK  %s\n' "$*"; }
warn() { printf '    WARN %s\n' "$*" >&2; }
die()  { printf '    FAIL %s\n' "$*" >&2; exit 1; }

require_compose() {
  if [[ ${#COMPOSE[@]} -eq 0 ]]; then
    die "Neither 'docker compose', 'docker-compose', nor 'podman-compose' is available"
  fi
  if [[ ! -f "${COMPOSE_FILE}" ]]; then
    die "docker-compose.yml not found at ${COMPOSE_FILE}"
  fi
}

compose() {
  require_compose
  (cd "${ROOT_DIR}" && "${COMPOSE[@]}" -f "${COMPOSE_FILE}" "$@")
}

ensure_env_file() {
  if [[ -f "${ENV_FILE}" ]]; then
    return 0
  fi
  if [[ ! -f "${ENV_EXAMPLE}" ]]; then
    die ".env.local missing and .env.example not found"
  fi
  log "Creating .env.local from .env.example"
  cp "${ENV_EXAMPLE}" "${ENV_FILE}"
  ok "Wrote ${ENV_FILE}"
}

# Export KEY=VALUE pairs from .env.local into the current shell.
# Skips comments and blank lines; does not evaluate shell expansions.
load_env_file() {
  local file="${1:-${ENV_FILE}}"
  [[ -f "${file}" ]] || return 0
  local line key value
  while IFS= read -r line || [[ -n "${line}" ]]; do
    # Trim leading/trailing whitespace.
    line="${line#"${line%%[![:space:]]*}"}"
    line="${line%"${line##*[![:space:]]}"}"
    [[ -z "${line}" || "${line}" == \#* ]] && continue
    [[ "${line}" == export\ * ]] && line="${line#export }"
    [[ "${line}" == *=* ]] || continue
    key="${line%%=*}"
    value="${line#*=}"
    key="${key%"${key##*[![:space:]]}"}"
    key="${key#"${key%%[![:space:]]*}"}"
    # Strip surrounding quotes.
    if [[ "${value}" =~ ^\".*\"$ || "${value}" =~ ^\'.*\'$ ]]; then
      value="${value:1:${#value}-2}"
    fi
    export "${key}=${value}"
  done < "${file}"
}

wait_for_service() {
  # wait_for_service <name> <host> <port> [timeout_seconds]
  local name="$1" host="$2" port="$3" timeout="${4:-60}"
  local start now
  start="$(date +%s)"
  log "Waiting for ${name} at ${host}:${port} (timeout ${timeout}s)"
  while true; do
    if (echo >/dev/tcp/"${host}"/"${port}") >/dev/null 2>&1; then
      ok "${name} is up"
      return 0
    fi
    # Fallback when /dev/tcp is unavailable (some shells).
    if command -v nc >/dev/null 2>&1 && nc -z "${host}" "${port}" >/dev/null 2>&1; then
      ok "${name} is up"
      return 0
    fi
    now="$(date +%s)"
    if (( now - start >= timeout )); then
      die "${name} did not become ready within ${timeout}s"
    fi
    sleep 1
  done
}

wait_for_compose_healthy() {
  # Poll docker compose until postgres + redis report healthy (or running if no health).
  local timeout="${1:-90}"
  local start now status
  start="$(date +%s)"
  log "Waiting for compose services to become healthy (timeout ${timeout}s)"
  while true; do
    if compose ps --format json >/dev/null 2>&1; then
      # docker compose v2 with json format
      status="$(compose ps --format json 2>/dev/null || true)"
      if echo "${status}" | grep -q '"Health":"healthy"' \
        || compose ps 2>/dev/null | grep -Eq 'healthy|Up'; then
        # Confirm both required ports.
        if (echo >/dev/tcp/127.0.0.1/5432) >/dev/null 2>&1 \
          && (echo >/dev/tcp/127.0.0.1/6379) >/dev/null 2>&1; then
          ok "postgres and redis are reachable"
          return 0
        fi
      fi
    else
      if (echo >/dev/tcp/127.0.0.1/5432) >/dev/null 2>&1 \
        && (echo >/dev/tcp/127.0.0.1/6379) >/dev/null 2>&1; then
        ok "postgres and redis are reachable"
        return 0
      fi
    fi
    now="$(date +%s)"
    if (( now - start >= timeout )); then
      compose ps || true
      die "Compose services did not become ready within ${timeout}s"
    fi
    sleep 2
  done
}

run_nx() {
  # Prefer pnpm nx from the monorepo; fall back to npx.
  if command -v pnpm >/dev/null 2>&1; then
    (cd "${ROOT_DIR}" && pnpm exec nx "$@")
  elif command -v npx >/dev/null 2>&1; then
    (cd "${ROOT_DIR}" && npx nx "$@")
  else
    die "Neither pnpm nor npx is available to run nx"
  fi
}

run_backend_poetry() {
  # Run a poetry command inside apps/backend with ROOT .env.local loaded.
  load_env_file
  (cd "${ROOT_DIR}/apps/backend" && poetry "$@")
}
