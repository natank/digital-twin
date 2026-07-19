# Development Guide

How to set up, run, test, and contribute code on the Digital Twin monorepo.

## Prerequisites

| Tool                 | Version  | Notes                                                                       |
| -------------------- | -------- | --------------------------------------------------------------------------- |
| Node.js              | 20+      | nvm recommended                                                             |
| pnpm                 | 10.x     | pinned via `packageManager` in `package.json` (Corepack)                    |
| Python               | 3.11+    | Poetry pins per-project via `.python-version`                               |
| Poetry               | 2.x      | `pipx install poetry`                                                       |
| poetry-plugin-export | latest   | **Required** for Nx Python build: `pipx inject poetry poetry-plugin-export` |
| Docker or Podman     | recent   | Compose-compatible CLI (`docker compose` works with Podman shims)           |
| pre-commit           | optional | `pipx install pre-commit`                                                   |
| `gh` CLI             | optional | GitHub PRs from the terminal                                                |

### Podman note

Some developer machines use Podman instead of Docker Desktop. With the
`docker` / `docker compose` CLI shims installed, `docker-compose.yml` and
`./scripts/start-dev.sh` work unchanged. Prefer:

```bash
docker compose ps
# equivalent: podman-compose ps
```

## First-time setup

```bash
git clone https://github.com/natank/digital-twin.git
cd digital-twin

# JavaScript workspace
corepack enable
pnpm install

# Python projects (in-project .venv via poetry.toml)
pnpm nx run apps/backend:install
pnpm nx run libs/backend-shared:install

# Environment
cp .env.example .env.local
python3 scripts/validate-env.py

# Optional: git hooks
pipx install pre-commit
pre-commit install
```

## One-command local stack

```bash
./scripts/start-dev.sh --seed
```

This:

1. Ensures `.env.local` exists
2. Validates env vars
3. Starts Postgres, Redis, LocalStack via Compose
4. Waits until healthy
5. Runs Alembic migrations (and seed with `--seed`)

Then start app servers in separate terminals:

```bash
pnpm nx serve apps/backend     # http://localhost:8000  (OpenAPI: /docs)
pnpm nx serve apps/frontend    # http://localhost:4200
pnpm nx run apps/backend:worker  # Celery worker (CV processing, etc.)
```

### Celery worker

Background tasks (CV extraction, profile summary) run in a Celery worker
backed by Redis. The API process **enqueues** work; the worker process
**executes** it.

```bash
# terminal A — API
pnpm nx serve apps/backend

# terminal B — worker (requires Redis from compose)
pnpm nx run apps/backend:worker
# equivalent:
#   cd apps/backend && poetry run celery -A src.worker.celery_app.celery_app worker -l INFO
```

Smoke-test without a live worker by setting `CELERY_TASK_ALWAYS_EAGER=true`
(pytest does this automatically via `conftest.py`).

Env vars (see `.env.example`):

| Variable                   | Purpose                          |
| -------------------------- | -------------------------------- |
| `CELERY_BROKER_URL`        | Redis broker (default DB 0)      |
| `CELERY_RESULT_BACKEND`    | Redis results (default DB 1)     |
| `CELERY_TASK_ALWAYS_EAGER` | In-process tasks (tests / debug) |

### Database helpers

```bash
./scripts/db-migrate.sh          # upgrade head
./scripts/db-migrate.sh down     # downgrade one revision
./scripts/db-seed.sh
./scripts/db-reset.sh --yes      # destroy local Postgres volume + remigrate/seed
```

## Project layout

```
apps/backend          FastAPI modular monolith (Poetry)
apps/frontend         React + Vite SPA
libs/backend-shared   Shared Python utilities (import: backend_shared)
libs/frontend-shared  Shared React components / types / utils
scripts/              Dev scripts (start-dev, db-*, validate-env, format, mypy)
docs/                 Requirements, design, phase plans
.github/workflows/    CI, Docker build, deploy scaffold
```

## Code style

| Language         | Formatter           | Linter | Types                |
| ---------------- | ------------------- | ------ | -------------------- |
| Python           | Black (100 cols)    | Flake8 | MyPy                 |
| TypeScript / TSX | Prettier (100 cols) | ESLint | `tsc` / Nx typecheck |

### Format

```bash
pnpm format              # Black + Prettier write
pnpm format:check        # CI-equivalent check mode
```

### Lint

```bash
pnpm lint                # flake8 (Nx) + ESLint
pnpm nx run-many --target=lint --all
pnpm exec eslint apps/frontend libs/frontend-shared
```

### Typecheck

```bash
pnpm typecheck           # TS (Nx) + Python (mypy)
pnpm nx run-many --target=typecheck --all
./scripts/run-mypy.sh
```

### Pre-commit

```bash
pre-commit run --all-files
```

Hooks run: trailing whitespace, YAML/JSON checks, Black, Flake8, Prettier,
MyPy, ESLint.

## Testing

Frontend uses **Vitest** (not Jest). Backend uses **pytest**.

```bash
# All Nx projects
pnpm nx run-many --target=test --all

# Individual
pnpm nx test apps/backend
pnpm nx test frontend
pnpm nx test frontend-shared
pnpm nx test libs/backend-shared

# Env validator (lives outside Nx projects)
apps/backend/.venv/bin/python -m pytest scripts/tests -v
```

Coverage artifacts:

- Python: `coverage/apps/backend/`, `coverage/libs/backend-shared/`
- Frontend: per-project Vitest coverage dirs under each app/lib

## Common Nx commands

```bash
pnpm nx graph
pnpm nx show projects
pnpm nx run-many --target=lint,test,typecheck,build --all
pnpm nx run apps/backend:migrate
pnpm nx run apps/backend:seed
```

## Docker images

Build from monorepo root (same as CI `build.yml`):

```bash
docker build -f apps/backend/Dockerfile -t digital-twin-backend .
docker build -f apps/frontend/Dockerfile -t digital-twin-frontend .
```

## Debugging

### VS Code / Cursor

Shared workspace config is committed under `.vscode/`:

- Python interpreter: `apps/backend/.venv/bin/python`
- Launch: Backend Uvicorn, pytest current file, validate-env
- Format on save: Black (Python), Prettier (TS/JS)

Install recommended extensions when prompted (see `.vscode/extensions.json`).

### Backend API

With the stack up and `pnpm nx serve apps/backend`:

- Health: `curl http://localhost:8000/health`
- Swagger UI: http://localhost:8000/docs

### Database

```bash
# Via compose
docker compose exec postgres psql -U postgres -d digital_twin_dev
```

## Git workflow

Branch naming (Phase 0):

```text
phase-0/{pr-number}-{short-description}
```

Later phases / epics:

```text
e1/001-auth-registration
phase-1/…
```

Commits: [Conventional Commits](https://www.conventionalcommits.org/) with optional scope:

```text
chore(phase-0): …
feat(auth): …
fix(profile): …
docs: …
```

PRs: use the GitHub template; squash-merge into `main`. See [CONTRIBUTING.md](./CONTRIBUTING.md).

## CI

On every PR and push to `main`:

| Check                                            | Workflow job                        |
| ------------------------------------------------ | ----------------------------------- |
| flake8, typecheck, black, mypy, eslint, prettier | `quality`                           |
| unit tests + coverage                            | `test`                              |
| Nx build                                         | `build`                             |
| Docker images                                    | `docker-backend`, `docker-frontend` |

Local parity:

```bash
pnpm format:check
pnpm lint
pnpm typecheck
pnpm nx run-many --target=test,build --all
```

## Common issues

### `poetry export` fails during Nx Python build

Install the export plugin:

```bash
pipx inject poetry poetry-plugin-export
```

### Compose / port already in use

```bash
docker compose ps
docker compose down
# or free 5432 / 6379 / 4566
```

### Backend can't find `.env.local`

Settings load from the **monorepo root** `.env.local`, not `apps/backend/.env.local`.

### `backend_shared` import errors

Install the shared library and backend (path dependency):

```bash
pnpm nx run libs/backend-shared:install
pnpm nx run apps/backend:install
```

Import as:

```python
from backend_shared import ValidationError, ApiResponse
```

### Frontend ESLint / Prettier not found

```bash
pnpm install
```

### Pre-commit mypy fails but IDE is fine

MyPy runs via Poetry envs in `scripts/run-mypy.sh`. Ensure those installs are current:

```bash
pnpm nx run apps/backend:install
pnpm nx run libs/backend-shared:install
./scripts/run-mypy.sh
```

## Related docs

- [CONTRIBUTING.md](./CONTRIBUTING.md) — PR process and review expectations
- [OPERATIONAL_CONCEPT.md](./OPERATIONAL_CONCEPT.md)
- [PRD.md](./PRD.md)
- [TECHNICAL_DESIGN.md](./TECHNICAL_DESIGN.md)
- [IMPLEMENTATION_MASTER_PLAN.md](./IMPLEMENTATION_MASTER_PLAN.md)
- [phase-0/PR_BREAKDOWN.md](./phase-0/PR_BREAKDOWN.md)
- [phase-1/PR_BREAKDOWN.md](./phase-1/PR_BREAKDOWN.md)
