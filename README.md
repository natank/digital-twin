# Digital Twin AI Assistant Platform

[![CI](https://github.com/natank/digital-twin/actions/workflows/ci.yml/badge.svg)](https://github.com/natank/digital-twin/actions/workflows/ci.yml)
[![Build](https://github.com/natank/digital-twin/actions/workflows/build.yml/badge.svg)](https://github.com/natank/digital-twin/actions/workflows/build.yml)

A 24/7 AI-powered digital twin that represents professionals on their websites, engaging visitors and answering career-related questions.

## Overview

Digital Twin enables professionals to create an always-available AI assistant that:

- Engages website visitors with intelligent conversations
- Represents career, background, skills, and experience
- Generates qualified leads through professional engagement
- Maintains consistent brand voice and boundaries

## Tech Stack

- **Backend:** FastAPI (Python 3.11+), PostgreSQL, Redis
- **Frontend:** React 19, TypeScript, Vite
- **AI/LLM:** Claude API
- **Notifications:** Pushover
- **Infrastructure:** Docker / Podman, Nx Monorepo

## Prerequisites

| Tool                 | Version  | Notes                                                                                          |
| -------------------- | -------- | ---------------------------------------------------------------------------------------------- |
| Node.js              | 20+      | via nvm or system install                                                                      |
| pnpm                 | 9+       | `corepack enable && corepack prepare pnpm@latest --activate`                                   |
| Python               | 3.11+    | Poetry pins per-project via `.python-version`                                                  |
| Poetry               | 2.x      | `pipx install poetry`                                                                          |
| poetry-plugin-export | latest   | `pipx inject poetry poetry-plugin-export` (required by Nx Python build)                        |
| Docker or Podman     | recent   | Needs a Compose CLI (see [Local infrastructure](#local-infrastructure-docker--podman-compose)) |
| `gh` CLI             | optional | GitHub PRs from the command line                                                               |

## Quick Start

```bash
# Clone
git clone https://github.com/yourusername/digital-twin.git
cd digital-twin

# Install JS + Python dependencies
pnpm install
pnpm nx run apps/backend:install
pnpm nx run libs/backend-shared:install

# Environment (git-ignored; template is .env.example)
cp .env.example .env.local
# Optional: set VITE_DEMO_OWNER_ID after seed (see seed output / DB)
python3 scripts/validate-env.py

# Infrastructure: Postgres, Redis, LocalStack (S3) via Compose
# Prefer the helper (validates env, compose up, wait healthy, migrate, optional seed):
./scripts/start-dev.sh --seed

# Or run Compose yourself (manual path) — see section below.

# In separate terminals — application servers (hot reload)
pnpm nx serve apps/backend     # http://localhost:8000  (docs: /docs)
pnpm nx serve apps/frontend    # http://localhost:4200
# Optional: Celery worker for CV processing
pnpm nx run apps/backend:worker
```

`.env.local` is git-ignored. `.env.example` is the committed template.

Validate services after the stack is up:

```bash
python3 scripts/validate-env.py --check-services
```

## Local infrastructure (Docker / Podman Compose)

The repo root **`docker-compose.yml`** defines local **infra** (not the API/UI):

| Service      | Port | Role                       |
| ------------ | ---- | -------------------------- |
| `postgres`   | 5432 | App database               |
| `redis`      | 6379 | Cache, rate limits, Celery |
| `localstack` | 4566 | Local AWS S3 (CV uploads)  |

### Compose CLI options

Any of these work if installed and able to talk to the container engine:

```bash
# Docker Desktop / Engine (Compose V2 plugin)
docker compose -f docker-compose.yml up -d
docker compose -f docker-compose.yml ps
docker compose -f docker-compose.yml down

# Standalone docker-compose binary
docker-compose -f docker-compose.yml up -d

# Podman (common on macOS without Docker Desktop)
podman machine start                    # required once per reboot if machine is stopped
podman-compose -f docker-compose.yml up -d
podman-compose -f docker-compose.yml ps
# Some installs also support:  podman compose -f docker-compose.yml up -d
```

`./scripts/start-dev.sh` auto-detects, in order: `docker compose` → `docker-compose` → `podman-compose`.

### Podman notes (macOS)

1. **Start the Podman VM** if you see “connection refused” / cannot connect to the Podman socket:

   ```bash
   podman machine list
   podman machine start
   ```

2. If `docker` is a symlink to `podman` and the API socket is not on the default path:

   ```bash
   export DOCKER_HOST="unix://$(podman machine inspect --format '{{.ConnectionInfo.PodmanSocket.Path}}')"
   ```

3. Install Compose for Podman if missing: `brew install podman-compose` (or enable the Compose provider for your Podman install).

### Manual Compose workflow (without start-dev.sh)

```bash
cp .env.example .env.local          # once
# Start containers
docker compose up -d                # or: podman-compose up -d
# Schema + sample owner
./scripts/db-migrate.sh
./scripts/db-seed.sh
# Apps
pnpm nx serve apps/backend
pnpm nx serve apps/frontend
```

Seed login (after `--seed` / `db-seed.sh`): `owner@example.com` / `Owner123!`  
For public `/chat`, set `VITE_DEMO_OWNER_ID` in `.env.local` to that owner’s UUID (from `/auth/me` after login or the DB).

### What start-dev.sh does

1. Ensures `.env.local` exists (from `.env.example` if needed)
2. Validates env vars
3. Runs **Compose `up -d`** for Postgres, Redis, LocalStack
4. Waits until Postgres/Redis are reachable
5. Runs Alembic migrations (and seed with `--seed`)

It does **not** start the FastAPI or Vite processes — run those with `pnpm nx serve` as above.

## Development scripts

| Script                            | Purpose                                                               |
| --------------------------------- | --------------------------------------------------------------------- |
| `./scripts/start-dev.sh`          | Create env (if needed), validate, `compose up`, wait healthy, migrate |
| `./scripts/start-dev.sh --seed`   | Same as above, then seed sample data                                  |
| `./scripts/db-migrate.sh`         | Alembic upgrade head (also: `down`, `history`, `current`)             |
| `./scripts/db-seed.sh`            | Idempotent sample owner + profile                                     |
| `./scripts/db-reset.sh`           | Destroy local Postgres volume, remigrate, reseed                      |
| `python3 scripts/validate-env.py` | Validate required env vars and formats                                |

npm/pnpm aliases (from package.json):

```bash
pnpm dev              # ./scripts/start-dev.sh
pnpm dev:seed         # ./scripts/start-dev.sh --seed
pnpm db:migrate
pnpm db:seed
pnpm db:reset
pnpm validate-env
```

### Database utilities

```bash
./scripts/db-migrate.sh          # upgrade head
./scripts/db-migrate.sh down     # downgrade one revision
./scripts/db-migrate.sh history
./scripts/db-seed.sh
./scripts/db-reset.sh --yes      # non-interactive clean slate
```

These wrap the Nx targets on `apps/backend` (`migrate`, `migrate-down`, `seed`).

## Project Structure

```
digital-twin/
├── apps/
│   ├── backend/          # FastAPI modular monolith
│   └── frontend/         # React + Vite SPA
├── libs/
│   ├── backend-shared/   # Python shared libraries (Phase 0 scaffold)
│   └── frontend-shared/  # React shared components (Phase 0 scaffold)
├── scripts/              # Local dev: start-dev, db-*, validate-env
├── docs/                 # Requirements, design, phase PR breakdowns
├── tools/                # Nx generators & future tooling
├── docker-compose.yml    # Postgres 14, Redis 7, LocalStack (S3)
├── .env.example          # Env template (copy → .env.local)
└── .vscode/              # Recommended editor settings / launch configs
```

## Documentation

- [Development Guide](./docs/DEVELOPMENT.md) — Setup, tooling, testing, debugging
- [Test Readiness Report](./docs/TEST_READINESS_REPORT.md) — Phase 0–3 validation and production-test readiness
- [Contributing](./docs/CONTRIBUTING.md) — PR process, commits, reviews
- [Operational Concept](./docs/OPERATIONAL_CONCEPT.md) — System overview and actors
- [Product Requirements](./docs/PRD.md) — Features and epics
- [Technical Design](./docs/TECHNICAL_DESIGN.md) — Architecture and implementation
- [Implementation Plan](./docs/IMPLEMENTATION_MASTER_PLAN.md) — Development roadmap
- [Phase 0 PR Breakdown](./docs/phase-0/PR_BREAKDOWN.md) — Foundation (complete)
- [Phase 1 PR Breakdown](./docs/phase-1/PR_BREAKDOWN.md) — Core services (Auth → Profile → Chat)
- [Phase 2 PR Breakdown](./docs/phase-2/PR_BREAKDOWN.md) — Notifications + config
- [Phase 3 PR Breakdown](./docs/phase-3/PR_BREAKDOWN.md) — Frontend SPA

## IDE setup

VS Code / Cursor recommended extensions are listed in `.vscode/extensions.json`
(accept the workspace recommendation prompt). Shared settings:

- Python interpreter: `apps/backend/.venv/bin/python`
- Format on save: Black (Python), Prettier (TS/JS)
- Debug configs: Backend Uvicorn, pytest current file, validate-env

EditorConfig (`.editorconfig`) provides the same baseline for other editors.

## Development guidelines

- **Code style:** Black (Python, 100 cols), Prettier (TypeScript/JSON/YAML/MD)
- **Linting:** Flake8 (Python), ESLint (TypeScript)
- **Type checking:** MyPy (Python), TypeScript (`tsc` / Nx typecheck)
- **Hooks:** `pre-commit install` (optional; see [DEVELOPMENT.md](./docs/DEVELOPMENT.md))
- **Testing:** pytest (backend), Vitest (frontend) — target ≥80% unit coverage
- **Commits:** Conventional commits, e.g. `chore(phase-0): …`, `feat(auth): …`
- **Git:** Feature branches, squash-merge via PR
- **Secrets:** Never commit `.env.local` or real API keys; placeholders only in `.env.example`

```bash
pnpm format          # write
pnpm format:check    # CI mode
pnpm lint
pnpm typecheck
```

### Branch naming (Phase 0)

```
phase-0/{pr-number}-{description}
# example: phase-0/003-development-environment
```

## Available Nx commands

```bash
# Application servers
pnpm nx serve apps/backend
pnpm nx serve apps/frontend

# Testing
pnpm nx test apps/backend
pnpm nx test apps/frontend
pnpm nx run-many --target=test --all

# Linting / typecheck / build
pnpm nx run-many --target=lint,typecheck,build --all

# Database (also via ./scripts/db-*.sh)
pnpm nx run apps/backend:migrate
pnpm nx run apps/backend:seed

# Dependency graph
pnpm nx graph
```

## CI/CD

GitHub Actions workflows live under `.github/workflows/`:

| Workflow   | File         | When                         | Purpose                                  |
| ---------- | ------------ | ---------------------------- | ---------------------------------------- |
| **CI**     | `ci.yml`     | PR + push to `main`          | Lint, typecheck, unit tests, Nx build    |
| **Build**  | `build.yml`  | PR + push to `main`          | Docker image builds (backend + frontend) |
| **Deploy** | `deploy.yml` | Manual (`workflow_dispatch`) | Staging/production scaffold (Phase 4)    |

```bash
# Local parity with CI quality gates
pnpm nx run-many --target=lint,test,typecheck,build --all

# Build container images (from monorepo root)
docker build -f apps/backend/Dockerfile -t digital-twin-backend .
docker build -f apps/frontend/Dockerfile -t digital-twin-frontend .
```

Status checks expected on `main` (branch protection): `quality`, `test`, `build`, `docker-backend`, `docker-frontend`.

## Architecture

See [Technical Design](./docs/TECHNICAL_DESIGN.md) for detailed diagrams.

**High-level flow:**

```
Owner uploads CV → Profile summary generated → Digital twin ready
                                                        ↓
                                           Visitor asks question
                                                        ↓
                                           AI responds with context
                                                        ↓
                                           Owner gets notification
```

## Pull request workflow

```bash
# Feature branch
git checkout -b phase-0/003-development-environment

# Open PR (body from local pr-work artifact)
gh pr create \
  --title "[Phase-0] PR-003 Development Environment" \
  --body "$(cat pr-work/PHASE0-003-development-environment/PR_DESCRIPTION.md)"

# Merge when approved
gh pr merge {number} --squash --delete-branch
```

See [Implementation Master Plan — PR guidelines](./docs/IMPLEMENTATION_MASTER_PLAN.md#pull-request-management-guidelines).

## Roadmap

| Phase | Focus                                                  | Status      |
| ----- | ------------------------------------------------------ | ----------- |
| **0** | Foundation (Nx, DB, dev env, CI, shared libs, tooling) | In progress |
| **1** | Core services (Auth → Profile → Chat)                  | Planned     |
| **2** | Supporting services (Notifications, Config)            | Planned     |
| **3** | Frontend (public pages, dashboard, chat UI)            | Planned     |
| **4** | Integration, hardening, alpha launch                   | Planned     |

## Support

- Bugs: `gh issue create --title "Bug: …"`
- Open PRs: `gh pr list --state open`

---

**Status:** MVP Development (Phase 0 — Foundation)  
**Last Updated:** 2026-07-19
