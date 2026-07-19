# Digital Twin AI Assistant Platform

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

| Tool | Version | Notes |
|------|---------|--------|
| Node.js | 20+ | via nvm or system install |
| pnpm | 9+ | `corepack enable && corepack prepare pnpm@latest --activate` |
| Python | 3.11+ | Poetry pins per-project via `.python-version` |
| Poetry | 2.x | `pipx install poetry` |
| poetry-plugin-export | latest | `pipx inject poetry poetry-plugin-export` (required by Nx Python build) |
| Docker or Podman | recent | Compose-compatible CLI (`docker compose` or shims) |
| `gh` CLI | optional | GitHub PRs from the command line |

## Quick Start

```bash
# Clone
git clone https://github.com/yourusername/digital-twin.git
cd digital-twin

# Install JS + Python dependencies
pnpm install
pnpm nx run apps/backend:install
pnpm nx run libs/backend-shared:install

# One-command infrastructure start (creates .env.local, starts Postgres/Redis/LocalStack, migrates)
./scripts/start-dev.sh --seed

# In separate terminals — application servers (hot reload)
pnpm nx serve apps/backend     # http://localhost:8000  (docs: /docs)
pnpm nx serve apps/frontend    # http://localhost:4200
```

### Environment setup

```bash
cp .env.example .env.local
# Edit .env.local if you need non-default credentials
python3 scripts/validate-env.py
python3 scripts/validate-env.py --check-services   # after stack is up
```

`.env.local` is git-ignored. `.env.example` is the committed template.

## Development scripts

| Script | Purpose |
|--------|---------|
| `./scripts/start-dev.sh` | Create env (if needed), validate, `compose up`, wait healthy, migrate |
| `./scripts/start-dev.sh --seed` | Same as above, then seed sample data |
| `./scripts/db-migrate.sh` | Alembic upgrade head (also: `down`, `history`, `current`) |
| `./scripts/db-seed.sh` | Idempotent sample owner + profile |
| `./scripts/db-reset.sh` | Destroy local Postgres volume, remigrate, reseed |
| `python3 scripts/validate-env.py` | Validate required env vars and formats |

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

- [Operational Concept](./docs/OPERATIONAL_CONCEPT.md) — System overview and actors
- [Product Requirements](./docs/PRD.md) — Features and epics
- [Technical Design](./docs/TECHNICAL_DESIGN.md) — Architecture and implementation
- [Implementation Plan](./docs/IMPLEMENTATION_MASTER_PLAN.md) — Development roadmap
- [Phase 0 PR Breakdown](./docs/phase-0/PR_BREAKDOWN.md) — Current foundation work

## IDE setup

VS Code / Cursor recommended extensions are listed in `.vscode/extensions.json`
(accept the workspace recommendation prompt). Shared settings:

- Python interpreter: `apps/backend/.venv/bin/python`
- Format on save: Black (Python), Prettier (TS/JS)
- Debug configs: Backend Uvicorn, pytest current file, validate-env

EditorConfig (`.editorconfig`) provides the same baseline for other editors.

## Development guidelines

- **Code style:** Black (Python, 100 cols), Prettier (TypeScript) — full lint config in Phase 0 PR-006
- **Type checking:** MyPy (Python), TypeScript (Frontend)
- **Testing:** pytest (backend), Vitest (frontend) — target ≥80% unit coverage
- **Commits:** Conventional commits, e.g. `chore(phase-0): …`, `feat(auth): …`
- **Git:** Feature branches, squash-merge via PR
- **Secrets:** Never commit `.env.local` or real API keys; placeholders only in `.env.example`

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

| Phase | Focus | Status |
|-------|--------|--------|
| **0** | Foundation (Nx, DB, dev env, CI, shared libs, tooling) | In progress |
| **1** | Core services (Auth → Profile → Chat) | Planned |
| **2** | Supporting services (Notifications, Config) | Planned |
| **3** | Frontend (public pages, dashboard, chat UI) | Planned |
| **4** | Integration, hardening, alpha launch | Planned |

## Support

- Bugs: `gh issue create --title "Bug: …"`
- Open PRs: `gh pr list --state open`

---

**Status:** MVP Development (Phase 0 — Foundation)  
**Last Updated:** 2026-07-19
