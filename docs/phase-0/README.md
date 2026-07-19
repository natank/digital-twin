# Phase 0: Foundation Setup

**Phase Duration:** Weeks 1-2 (10 working days)  
**Start Date:** 2026-07-22 (after baseline docs PR merged)  
**Goal:** One-command local development environment with CI/CD pipeline ready

---

## Overview

Phase 0 establishes the infrastructure foundation for all development work. This phase focuses on:

✅ **Nx Monorepo** — Initialize frontend + backend + shared libraries structure  
✅ **Database & Infrastructure** — PostgreSQL, Redis, Docker Compose setup  
✅ **Development Environment** — Local dev scripts and configuration  
✅ **CI/CD Pipeline** — GitHub Actions workflows for testing and building  
✅ **Shared Libraries** — Backend and frontend common code  
✅ **Development Tooling** — Linting, formatting, testing configuration  

---

## Phase 0 Documentation

### [PR_BREAKDOWN.md](./PR_BREAKDOWN.md)
**Comprehensive guide to all 6 PRs in Phase 0**

Contains:
- Detailed breakdown of each PR (PR-001 through PR-006)
- Scope, deliverables, and acceptance criteria for each
- File structure and configuration details
- Dependencies and integration points
- Timeline and team assignments
- Success criteria and sign-off checklist

**Start here** → Read PR_BREAKDOWN.md for complete Phase 0 plan

---

## Phase 0 PRs Overview

### PR-001: Nx Monorepo Initialization
**Weeks 1-2 | 2-3 days | ~200-400 lines**

Initialize the Nx workspace with:
- Backend app (FastAPI + Python)
- Frontend app (React + TypeScript)
- Backend shared library
- Frontend shared library
- Tools directory for scripts/generators

[Full Details](./PR_BREAKDOWN.md#pr-001-nx-monorepo-initialization)

---

### PR-002: Database & Infrastructure
**Weeks 1-2 | 2 days | ~300-500 lines**

Set up persistent data layer:
- PostgreSQL 14 with initial schema (Owners, Profiles, Sessions)
- Alembic migration framework
- Docker Compose stack (PostgreSQL, Redis, LocalStack)
- Database initialization and seed scripts

[Full Details](./PR_BREAKDOWN.md#pr-002-database--infrastructure)

---

### PR-003: Development Environment
**Weeks 1-2 | 1-2 days | ~150-250 lines**

Configure local development:
- Environment variables (.env.local)
- Development startup scripts
- Database utility scripts (migrate, seed, reset)
- IDE configuration (.vscode)
- Editor configuration (.editorconfig)

[Full Details](./PR_BREAKDOWN.md#pr-003-development-environment)

---

### PR-004: CI/CD Pipeline
**Weeks 1-2 | 2 days | ~400-600 lines**

Set up GitHub Actions workflows:
- CI workflow (linting, type checking, tests)
- Build workflow (Docker image builds)
- Deploy workflow (scaffold for Phase 4)
- Branch protection rules
- Status badges

[Full Details](./PR_BREAKDOWN.md#pr-004-cicd-pipeline)

---

### PR-005: Shared Libraries
**Weeks 1-2 | 2 days | ~200-400 lines**

Create reusable code packages:
- Backend shared: database, exceptions, schemas, dependencies, utils
- Frontend shared: components, hooks, types, utils
- Proper exports and imports

[Full Details](./PR_BREAKDOWN.md#pr-005-shared-libraries)

---

### PR-006: Development Tooling & Documentation
**Weeks 1-2 | 1-2 days | ~300-500 lines**

Configure quality tools and documentation:
- Black, Flake8, MyPy (Python linting/formatting)
- ESLint, Prettier (TypeScript linting/formatting)
- Pre-commit hooks
- Pytest and Jest configuration
- DEVELOPMENT.md and CONTRIBUTING.md guides

[Full Details](./PR_BREAKDOWN.md#pr-006-development-tooling--documentation)

---

## Success Criteria

Phase 0 is complete when:

### Infrastructure ✅
- [ ] Nx monorepo initialized and all projects listed
- [ ] Docker Compose stack running (Postgres, Redis, LocalStack)
- [ ] Database schema created with Alembic migrations
- [ ] All initial database entities exist (Owners, Profiles, Sessions)

### Development ✅
- [ ] One command starts dev: `./scripts/start-dev.sh`
- [ ] All environment variables validated
- [ ] Database migration/seed scripts working
- [ ] IDE auto-formatting configured
- [ ] Hot reload working for backend and frontend

### Quality & Testing ✅
- [ ] All linting tools passing (Black, Flake8, ESLint, Prettier)
- [ ] Type checking passing (MyPy, TypeScript)
- [ ] GitHub Actions CI/CD pipeline active
- [ ] Branch protection rules enforced
- [ ] Pre-commit hooks working

### Code & Documentation ✅
- [ ] Backend shared library importable
- [ ] Frontend shared library importable
- [ ] DEVELOPMENT.md complete and accurate
- [ ] CONTRIBUTING.md complete and accurate
- [ ] README updated with Phase 0 status
- [ ] All PR artifacts archived

### Team ✅
- [ ] All team members can run dev environment locally
- [ ] All team members understand dev workflow
- [ ] All team members can create/review PRs using `gh`
- [ ] No blockers for Phase 1 start

---

## PR Management Process

### For Each PR:

1. **Create feature branch**
   ```bash
   git checkout -b phase-0/{pr-number}-{description}
   # Example: phase-0/001-nx-monorepo
   ```

2. **Create pr-work folder**
   ```bash
   mkdir -p pr-work/PHASE0-{number}-{feature}
   # Add: PR_DESCRIPTION.md, CHECKLIST.md, FINDINGS.md, ARTIFACTS/
   ```

3. **Commit with clear message**
   ```bash
   git commit -m "chore(phase-0): PR-{number} Description"
   ```

4. **Create PR**
   ```bash
   gh pr create \
     --title "[Phase-0] PR-{number} Description" \
     --body "$(cat pr-work/PHASE0-{number}-{feature}/PR_DESCRIPTION.md)"
   ```

5. **Review and merge**
   ```bash
   gh pr review {number} --approve
   gh pr merge {number} --squash --delete-branch
   ```

---

## Timeline

```
Week 1 (Mon-Fri):
├── Mon-Tue: PR-001 (Nx Monorepo)
├── Tue-Wed: PR-002 (Database) + PR-004 (CI/CD)
├── Wed-Thu: PR-003 (Dev Env) + PR-005 (Shared Libs)
└── Thu-Fri: PR-006 (Tooling) + Testing

Week 2 (Mon-Fri):
├── Mon-Tue: Address any issues from Week 1 PRs
├── Tue-Wed: Integration testing across all PRs
├── Wed-Thu: Team training and process alignment
├── Thu-Fri: Phase 1 planning and PR-001 creation
```

---

## Parallel Work Strategy

**Recommended for team of 4:**

1. **Developer 1:** PR-001 (Nx) + PR-004 (CI/CD)
2. **Developer 2:** PR-002 (Database) + PR-003 (Dev Env)
3. **Developer 3:** PR-005 (Shared Libs) + support
4. **Developer 4:** PR-006 (Tooling) + documentation

**Key constraint:** PR-001 must complete before others can start (most others depend on it)

---

## Dependency Graph

```
PR-001 (Nx Setup) ← REQUIRED for all others
    ↓
    ├→ PR-002 (Database)
    ├→ PR-004 (CI/CD)
    ├→ PR-005 (Shared Libs)
    └→ PR-003 & PR-006 (can work in parallel)
    
Once all merged:
    ↓
./scripts/start-dev.sh
    ↓
One-click local development ✅
```

---

## Getting Help

### Resources
- **PR Breakdown Details:** See [PR_BREAKDOWN.md](./PR_BREAKDOWN.md)
- **Architecture Reference:** See [docs/TECHNICAL_DESIGN.md](../TECHNICAL_DESIGN.md)
- **Implementation Plan:** See [docs/IMPLEMENTATION_MASTER_PLAN.md](../IMPLEMENTATION_MASTER_PLAN.md)

### Common Questions
- **How do I start working on a PR?** → See "PR Management Process" section above
- **What if PR-X is blocked?** → Document in pr-work/FINDINGS.md and ask in standup
- **How do I run tests locally?** → Wait for PR-004 (CI/CD) to complete, then use pytest/jest
- **Where do I put configuration?** → .env.local (git ignored) for secrets, .env.example for public

---

## Moving to Phase 1

Once Phase 0 is complete:
- ✅ All 6 PRs merged to main
- ✅ Infrastructure fully operational
- ✅ Team trained and aligned
- ✅ No blockers identified

**Then:** Create `docs/phase-1/PR_BREAKDOWN.md` and begin Phase 1 (Core Services)

**Estimated start:** End of Week 2 (2026-07-26)

---

## Related Documentation

- [Implementation Master Plan](../IMPLEMENTATION_MASTER_PLAN.md) — 16-week roadmap
- [Technical Design](../TECHNICAL_DESIGN.md) — Architecture and design
- [PR Management Guidelines](../IMPLEMENTATION_MASTER_PLAN.md#pull-request-management-guidelines) — PR workflow
- [GitHub CLI Workflow](../IMPLEMENTATION_MASTER_PLAN.md#github-command-line-gh-workflow) — Using `gh` CLI

---

**Last Updated:** 2026-07-19  
**Status:** Draft (awaiting baseline docs PR merge)  
**Next:** Phase 1 documentation upon Phase 0 completion
