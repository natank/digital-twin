# Phase 0: Quick Reference

**Phase Duration:** Weeks 1-2  
**Goal:** Foundation infrastructure ready for Phase 1  

---

## 6 PRs at a Glance

```
┌─────────────────────────────────────────────────────────────┐
│ Phase 0: Foundation Setup (6 PRs, 10 working days)          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  PR-001: Nx Monorepo          [███░░░░░░] 2-3 days         │
│  └─ Initialize project structure                            │
│                                                              │
│  PR-002: Database             [███░░░░░░] 2 days            │
│  └─ PostgreSQL + Alembic + Docker                           │
│                                                              │
│  PR-003: Dev Environment      [██░░░░░░░] 1-2 days         │
│  └─ .env, startup scripts, IDE config                       │
│                                                              │
│  PR-004: CI/CD Pipeline       [███░░░░░░] 2 days            │
│  └─ GitHub Actions + branch protection                      │
│                                                              │
│  PR-005: Shared Libraries     [███░░░░░░] 2 days            │
│  └─ Backend + Frontend shared code                          │
│                                                              │
│  PR-006: Tooling              [███░░░░░░] 1-2 days          │
│  └─ Black, ESLint, MyPy, documentation                      │
│                                                              │
│  TOTAL: ~1,550-2,650 lines across 6 PRs                     │
└─────────────────────────────────────────────────────────────┘
```

---

## PR-001: Nx Monorepo

**What:** Initialize Nx workspace  
**Creates:**
- `apps/backend/` — FastAPI app
- `apps/frontend/` — React app
- `libs/backend-shared/` — Python shared lib
- `libs/frontend-shared/` — TypeScript shared lib
- `nx.json`, `package.json`, `pyproject.toml`

**Commands to verify:**
```bash
nx graph
nx list
pnpm nx show projects
```

---

## PR-002: Database & Infrastructure

**What:** Set up PostgreSQL + Docker Compose  
**Creates:**
- Alembic migration structure
- Initial schema: Owners, OwnerSessions, Profiles
- `docker-compose.yml` (Postgres, Redis, LocalStack)
- `db-init.sql`, `seed-data.sql`

**Commands to verify:**
```bash
docker-compose up -d
docker-compose ps
psql -h localhost -U postgres -d digital_twin_dev
alembic upgrade head
```

---

## PR-003: Dev Environment

**What:** Local development configuration  
**Creates:**
- `.env.local` (git ignored)
- `scripts/start-dev.sh`
- `scripts/db-migrate.sh`, `db-seed.sh`, `db-reset.sh`
- `.vscode/settings.json`
- `.editorconfig`

**One command to start:**
```bash
./scripts/start-dev.sh
```

---

## PR-004: CI/CD Pipeline

**What:** GitHub Actions workflows  
**Creates:**
- `.github/workflows/ci.yml` (test, lint, type check)
- `.github/workflows/build.yml` (Docker builds)
- `.github/workflows/deploy.yml` (scaffold)
- Branch protection rules

**Runs on:** Every PR push

---

## PR-005: Shared Libraries

**What:** Reusable code packages  
**Backend shared:**
- `database.py` — DB sessions
- `exceptions.py` — Custom exceptions
- `schemas.py` — Base Pydantic models
- `dependencies.py` — DI setup
- `utils.py` — Helpers

**Frontend shared:**
- `components/` — UI components
- `hooks/` — React hooks
- `types/` — TypeScript types
- `utils/` — Utilities

---

## PR-006: Tooling

**What:** Code quality & documentation  
**Configures:**
- Black (Python formatter)
- Flake8 (Python linter)
- MyPy (Python types)
- ESLint (TypeScript linter)
- Prettier (JavaScript formatter)
- Pre-commit hooks
- Pytest + Jest

**Creates:**
- `DEVELOPMENT.md`
- `CONTRIBUTING.md`

---

## Checklist for Phase 0 Complete

- [ ] PR-001 merged: Nx workspace ready
- [ ] PR-002 merged: Database + Docker working
- [ ] PR-003 merged: Dev env script working
- [ ] PR-004 merged: CI/CD active
- [ ] PR-005 merged: Shared libraries importable
- [ ] PR-006 merged: Tooling configured
- [ ] `./scripts/start-dev.sh` works one-click
- [ ] All team members can run locally
- [ ] No blockers for Phase 1

---

## Common Commands

```bash
# Start everything
./scripts/start-dev.sh

# Database operations
./scripts/db-migrate.sh
./scripts/db-seed.sh
./scripts/db-reset.sh

# Check services
docker-compose ps
redis-cli ping

# Run tests
pytest apps/backend/tests
jest apps/frontend

# Code quality
black apps/backend
flake8 apps/backend
mypy apps/backend
eslint apps/frontend/src
prettier apps/frontend/src

# Git workflow
git checkout -b phase-0/001-nx-monorepo
gh pr create --title "[Phase-0] PR-001 ..."
gh pr review 1 --approve
gh pr merge 1 --squash --delete-branch
```

---

## Timeline Overview

```
Week 1:
├─ Mon-Tue: PR-001 (Nx) ✓
├─ Tue-Wed: PR-002 (DB) + PR-004 (CI/CD) ✓
├─ Wed-Thu: PR-003 (Dev) + PR-005 (Libs) ✓
└─ Fri: PR-006 (Tooling) ✓

Week 2:
├─ Mon: Integration testing
├─ Tue: Fix any issues
├─ Wed: Team training
├─ Thu: Phase 1 planning
└─ Fri: Phase 1 PR-001 created
```

---

## Phase 0 → Phase 1 Transition

Once all 6 PRs merged and working:

1. ✅ Verify `./scripts/start-dev.sh` works for all team
2. ✅ Create `docs/phase-1/PR_BREAKDOWN.md`
3. ✅ Plan Phase 1 PRs (Auth → Profile → Chat)
4. ✅ Begin PR-001 of Phase 1

**Estimated:** End of Week 2 (2026-07-26)

---

## Help & Resources

- **Full Details:** [PR_BREAKDOWN.md](./PR_BREAKDOWN.md)
- **Architecture:** [docs/TECHNICAL_DESIGN.md](../TECHNICAL_DESIGN.md)
- **Roadmap:** [docs/IMPLEMENTATION_MASTER_PLAN.md](../IMPLEMENTATION_MASTER_PLAN.md)
- **PR Guidelines:** [PR Management section](../IMPLEMENTATION_MASTER_PLAN.md#pull-request-management-guidelines)

---

**Status:** Phase 0 ready to begin upon baseline docs PR merge  
**Baseline PR:** #1 ([Docs] Baseline project documentation)
