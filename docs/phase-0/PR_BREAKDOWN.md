# Phase 0: Foundation Setup - PR Breakdown

**Phase Duration:** Weeks 1-2 (10 working days)  
**Objective:** Establish infrastructure, configuration, and development environment foundations  
**Success Criteria:** One-command local development environment, CI/CD pipeline ready, database initialized

---

## Overview

Phase 0 consists of **6 interconnected PRs** that build the foundation for all development work:

```
Phase 0 Timeline:
Week 1 (development, parallel after PR-001):
├── PR-001: Nx Monorepo Setup            ← must merge first
├── PR-002: Database & Infrastructure
├── PR-003: Development Environment
├── PR-004: CI/CD Pipeline
├── PR-005: Shared Libraries
└── PR-006: Development Tooling & Documentation

Week 2:
├── Integration testing across all PRs
├── Fixes and blocker resolution
└── Team alignment + Phase 1 planning
```

---

## PR Breakdown Summary

| PR # | Title | Scope | Lines | Days | Priority |
|------|-------|-------|-------|------|----------|
| **001** | Nx Monorepo Initialization | Build system setup | 200-400 | 2 | P0 Critical |
| **002** | Database & Infrastructure | DB schema, Docker setup | 300-500 | 2 | P0 Critical |
| **003** | Development Environment | Config, env variables | 150-250 | 1-2 | P1 High |
| **004** | CI/CD Pipeline | GitHub Actions, tests | 400-600 | 2 | P0 Critical |
| **005** | Shared Libraries | Backend/frontend shared code | 200-400 | 2 | P1 High |
| **006** | Development Tooling | Scripts, linting, docs | 300-500 | 1-2 | P2 Medium |

**Total Scope:** ~1,550-2,650 lines of code/config across 6 PRs

---

## PR-001: Nx Monorepo Initialization

### Objective
Set up the Nx monorepo structure with Python backend and React frontend scaffolding.

### Scope
- [ ] Initialize Nx workspace with pnpm
- [ ] Configure Nx.json for Python + TypeScript
- [ ] Create apps/backend directory structure
- [ ] Create apps/frontend directory structure
- [ ] Create libs/backend-shared structure
- [ ] Create libs/frontend-shared structure
- [ ] Add TypeScript configuration
- [ ] Add Python pyproject.toml (Poetry)
- [ ] Create tools/ directory for generators/scripts

### Files to Create
```
nx.json
package.json
poetry.lock
pnpm-workspace.yaml

apps/backend/
├── pyproject.toml
├── src/
│   └── __init__.py
└── README.md

apps/frontend/
├── package.json
├── tsconfig.json
├── vite.config.ts
└── src/
    └── main.tsx

libs/backend-shared/
├── pyproject.toml
└── src/
    └── __init__.py

libs/frontend-shared/
├── package.json
└── src/
    └── index.ts

tools/
├── generators/
└── scripts/
```

### Dependencies
- Node.js 20+ installed
- pnpm installed
- Python 3.11+ installed
- poetry installed

### Validation
```bash
# Should work
nx graph
nx list
pnpm nx show projects
poetry --version
python --version
```

### Testing
- [ ] Nx workspace created successfully
- [ ] All projects listed with `nx list`
- [ ] No circular dependencies
- [ ] Dependency graph visible with `nx graph`

### Related Issues
Foundation for all other Phase 0 PRs

### Estimated Effort
**2 days** — 200-400 lines of config

---

## PR-002: Database & Infrastructure

### Objective
Set up PostgreSQL schema with Alembic migrations, Redis configuration, and docker-compose for local development.

### Scope
- [ ] Create Alembic migration structure
- [ ] Define initial database schema:
  - [ ] Owners table
  - [ ] OwnerSessions table
  - [ ] Profiles table
  - [ ] Create migration script
- [ ] Create docker-compose.yml with:
  - [ ] PostgreSQL service (v14)
  - [ ] Redis service (v7)
  - [ ] LocalStack (S3 simulation)
- [ ] Create database initialization scripts
- [ ] Add db-init.sql (seed data for development)
- [ ] Create .env.example with database variables

### Files to Create
```
apps/backend/
├── migrations/
│   ├── env.py
│   ├── alembic.ini
│   └── versions/
│       └── 001_initial_schema.py
└── scripts/
    ├── db-init.sql
    └── seed-data.sql

docker-compose.yml
.env.example
```

### Database Schema (Phase 0)
```python
# Owners
- id: UUID (PK)
- email: string (unique)
- password_hash: string
- first_name: string
- last_name: string
- is_active: bool
- email_verified: bool
- oauth_provider: string (nullable)
- oauth_id: string (nullable)
- created_at: DateTime
- updated_at: DateTime

# OwnerSessions
- id: UUID (PK)
- owner_id: UUID (FK)
- token: string (unique)
- expires_at: DateTime
- created_at: DateTime

# Profiles
- id: UUID (PK)
- owner_id: UUID (FK, unique)
- bio: string
- headline: string
- cv_file_path: string (nullable)
- cv_extracted_text: string (nullable)
- profile_summary: JSON (nullable)
- skills: JSON
- experience_years: int
- created_at: DateTime
- updated_at: DateTime
```

### Docker Services
```yaml
postgres:
  image: postgres:14
  ports: 5432:5432
  environment: POSTGRES_DB=digital_twin_dev

redis:
  image: redis:7
  ports: 6379:6379

localstack:  # For S3 simulation in dev
  image: localstack/localstack
  ports: 4566:4566
  environment: SERVICES=s3
```

### Validation
```bash
# Services running
docker-compose up -d
docker-compose ps

# Database accessible
psql -h localhost -U postgres -d digital_twin_dev
redis-cli ping

# Migrations run
alembic upgrade head
```

### Testing
- [ ] Database schema created correctly
- [ ] Migration can be run and rolled back
- [ ] All indexes created
- [ ] Foreign keys working
- [ ] Docker services start/stop cleanly

### Related Issues
Dependency for PR-003, PR-004

### Estimated Effort
**2 days** — 300-500 lines (SQL + YAML + Python)

---

## PR-003: Development Environment

### Objective
Configure local development setup with environment variables, development scripts, and IDE/tool configuration.

### Scope
- [ ] Create .env.local template with all required variables
- [ ] Create env validation script
- [ ] Create development startup script (start-dev.sh)
- [ ] Create database utility scripts:
  - [ ] db-migrate.sh (run migrations)
  - [ ] db-seed.sh (seed test data)
  - [ ] db-reset.sh (clean slate)
- [ ] Create .vscode/settings.json for IDE
- [ ] Create .editorconfig
- [ ] Create development guidelines in README

### Files to Create
```
.env.local (git ignored)
.env.example

scripts/
├── start-dev.sh
├── db-migrate.sh
├── db-seed.sh
├── db-reset.sh
└── validate-env.py

.vscode/
├── settings.json
├── extensions.json
└── launch.json

.editorconfig
```

### Environment Variables
```
DATABASE_URL=postgresql://postgres:password@localhost:5432/digital_twin_dev
REDIS_URL=redis://localhost:6379
JWT_SECRET=dev-secret-only-for-testing
JWT_EXPIRY=86400
PYTHONUNBUFFERED=1
DEBUG=true
LOG_LEVEL=DEBUG

# External services (placeholders for Phase 0)
CLAUDE_API_KEY=sk-test
PUSHOVER_APP_TOKEN=test-token
S3_BUCKET=digital-twin-dev
AWS_ENDPOINT_URL=http://localhost:4566
```

### Development Scripts
```bash
# Start everything
./scripts/start-dev.sh
# - Starts docker-compose
# - Runs migrations
# - Displays status

# Database operations
./scripts/db-migrate.sh
./scripts/db-seed.sh
./scripts/db-reset.sh
```

### IDE Configuration
```json
// .vscode/settings.json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/venv/bin/python",
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": false,
  "python.linting.flake8Enabled": true,
  "python.formatting.provider": "black",
  "editor.formatOnSave": true,
  "editor.defaultFormatter": "ms-python.python",
  "[python]": {
    "editor.defaultFormatter": "ms-python.python",
    "editor.formatOnSave": true
  },
  "[typescript]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode",
    "editor.formatOnSave": true
  }
}
```

### Validation
```bash
# Can validate env
python scripts/validate-env.py

# Can start dev environment
./scripts/start-dev.sh

# Services are accessible
pg_isready -h localhost -p 5432   # postgres
redis-cli -h localhost ping        # redis
```

### Testing
- [ ] All env variables read correctly
- [ ] Validation script works
- [ ] Start script runs without errors
- [ ] Database migration runs
- [ ] Services accessible
- [ ] IDE auto-formatting works

### Related Issues
Dependency for Phase 1 development

### Estimated Effort
**1-2 days** — 150-250 lines (shell + config)

---

## PR-004: CI/CD Pipeline

### Objective
Set up GitHub Actions workflows for testing, linting, and building across Python backend and TypeScript frontend.

### Scope
- [ ] Create CI workflow (.github/workflows/ci.yml):
  - [ ] Python linting (flake8, black, mypy)
  - [ ] TypeScript linting (ESLint, Prettier)
  - [ ] Python type checking
  - [ ] Unit tests (pytest + coverage)
  - [ ] Frontend tests (Jest)
- [ ] Create build workflow (.github/workflows/build.yml):
  - [ ] Backend Docker build
  - [ ] Frontend Docker build
- [ ] Create deploy workflow (scaffold only):
  - [ ] Deploy to staging (manual approval)
- [ ] Set up branch protection rules
- [ ] Add status badges to README

### Workflows to Create
```
.github/workflows/
├── ci.yml              # Run on every PR
├── build.yml           # Build on PR + main merge
└── deploy.yml          # Deploy (scaffold for Phase 4)
```

### CI Workflow (ci.yml)
```yaml
on: [pull_request, push to main]

jobs:
  lint-backend:
    - black --check .
    - flake8 apps/backend
    - mypy apps/backend
  
  lint-frontend:
    - eslint apps/frontend/src
    - prettier --check apps/frontend/src
  
  test-backend:
    - pytest apps/backend/tests --cov
    - Upload coverage to Codecov
  
  test-frontend:
    - jest apps/frontend --coverage
```

### Build Workflow (build.yml)
```yaml
on: [pull_request]

jobs:
  build-backend:
    - docker build apps/backend
  
  build-frontend:
    - docker build apps/frontend
```

### Branch Protection Rules
```
For main branch:
- Require PR reviews (min 1)
- Dismiss stale approvals
- Require status checks (CI passing)
- Require branches up to date
- Restrict who can push (admin only)
```

### Files to Create
```
.github/
├── workflows/
│   ├── ci.yml
│   ├── build.yml
│   └── deploy.yml (scaffold)
├── pull_request_template.md
└── CODEOWNERS
```

### Validation
```bash
# Push to feature branch
# Should see CI checks running

# View workflow
gh workflow list
gh workflow view ci
```

### Testing
- [ ] CI runs on PR creation
- [ ] All checks pass on valid code
- [ ] Checks fail on linting errors
- [ ] Code coverage reports generated
- [ ] Branch protection rules enforced

### Related Issues
Enables quality gates for all future PRs

### Estimated Effort
**2 days** — 400-600 lines (YAML + config)

---

## PR-005: Shared Libraries

### Objective
Create shared code libraries for backend and frontend to avoid duplication and improve consistency.

### Scope

### Backend Shared Library (libs/backend-shared)
- [ ] database.py — Database session factory
- [ ] exceptions.py — Custom exception classes
- [ ] schemas.py — Pydantic base models
- [ ] dependencies.py — Dependency injection setup
- [ ] utils.py — Common utilities (encryption, validation)
- [ ] logging.py — Logging configuration
- [ ] __init__.py — Package exports

### Frontend Shared Library (libs/frontend-shared)
- [ ] components/ — Common UI components (Button, Input, Modal, etc.)
- [ ] hooks/ — React hooks (useAuth, useApi, etc.)
- [ ] types/ — TypeScript type definitions
- [ ] utils/ — Utility functions
- [ ] __init__.ts — Exports

### Backend Shared Code
```python
# database.py
class Database:
    @staticmethod
    def get_session():
        """Dependency for DB access"""
        
# exceptions.py
class ValidationError(Exception):
class DatabaseError(Exception):
class AuthenticationError(Exception):

# schemas.py
class BaseSchema(BaseModel):
    class Config:
        from_attributes = True

# dependencies.py
async def get_current_user(token: str) -> User:
    """Auth dependency"""

# utils.py
def encrypt_field(value: str) -> str:
def decrypt_field(encrypted: str) -> str:
def validate_email(email: str) -> bool:
```

### Frontend Shared Code
```typescript
// hooks/useAuth.ts
export const useAuth = () => { ... }

// hooks/useApi.ts
export const useApi = () => { ... }

// components/Button.tsx
export const Button = ({ ... }) => { ... }

// components/Input.tsx
export const Input = ({ ... }) => { ... }

// types/index.ts
export type Owner = { ... }
export type Profile = { ... }
```

### Files to Create
```
libs/backend-shared/
├── src/
│   ├── __init__.py
│   ├── database.py
│   ├── exceptions.py
│   ├── schemas.py
│   ├── dependencies.py
│   ├── utils.py
│   ├── logging.py
│   └── types.py
└── pyproject.toml

libs/frontend-shared/
├── src/
│   ├── index.ts
│   ├── components/
│   │   ├── index.ts
│   │   ├── Button.tsx
│   │   ├── Input.tsx
│   │   └── Modal.tsx
│   ├── hooks/
│   │   ├── index.ts
│   │   ├── useAuth.ts
│   │   └── useApi.ts
│   ├── types/
│   │   └── index.ts
│   └── utils/
│       ├── index.ts
│       └── validators.ts
└── package.json
```

### Validation
```bash
# Backend shared imports work
python -c "from backend_shared import Database"

# Frontend shared imports work
import { Button } from '@libs/frontend-shared'

# No circular dependencies
nx graph
```

### Testing
- [ ] Backend shared library imports correctly
- [ ] Frontend shared library imports correctly
- [ ] Type hints work properly
- [ ] Exports are correct
- [ ] No circular dependencies
- [ ] Can be used by other packages

### Related Issues
Foundation for Phase 1 services

### Estimated Effort
**2 days** — 200-400 lines (Python + TypeScript)

---

## PR-006: Development Tooling & Documentation

### Objective
Set up code quality tools, linting configuration, and development guidelines.

### Scope
- [ ] Add Black configuration (pyproject.toml)
- [ ] Add Flake8 configuration (.flake8)
- [ ] Add MyPy configuration (mypy.ini)
- [ ] Add ESLint configuration (.eslintrc.json)
- [ ] Add Prettier configuration (.prettierrc)
- [ ] Add pre-commit hooks (.pre-commit-config.yaml)
- [ ] Add pytest configuration (pyproject.toml)
- [ ] Add Jest configuration (jest.config.js)
- [ ] Create DEVELOPMENT.md guide
- [ ] Create CONTRIBUTING.md guidelines

### Files to Create
```
pyproject.toml (update with tool configs)
.flake8
mypy.ini
.eslintrc.json
.prettierrc
.pre-commit-config.yaml
jest.config.js
tsconfig.json (update)

docs/
├── DEVELOPMENT.md
└── CONTRIBUTING.md
```

### Configuration Details

**Black (Python formatter):**
```toml
[tool.black]
line-length = 100
target-version = ['py311']
extend-exclude = '''
/venv/
'''
```

**Flake8 (Python linter):**
```ini
[flake8]
max-line-length = 100
extend-ignore = E203, W503
exclude = venv,__pycache__,.git
```

**MyPy (Python type checker):**
```ini
[mypy]
python_version = 3.11
warn_return_any = True
warn_unused_configs = True
disallow_untyped_defs = True
```

**ESLint (TypeScript linter):**
```json
{
  "extends": ["eslint:recommended", "plugin:@typescript-eslint/recommended"],
  "parser": "@typescript-eslint/parser",
  "plugins": ["@typescript-eslint"],
  "rules": {
    "@typescript-eslint/explicit-function-return-type": "error"
  }
}
```

**Pre-commit Hooks:**
```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black
  - repo: https://github.com/PyCQA/flake8
    hooks:
      - id: flake8
  - repo: https://github.com/pre-commit/mirrors-prettier
    hooks:
      - id: prettier
```

### Development Guide (DEVELOPMENT.md)
- Environment setup
- Running tests
- Code style
- Git workflow
- Debugging
- Common issues

### Contributing Guide (CONTRIBUTING.md)
- Code of conduct
- How to contribute
- PR process
- Commit conventions
- Review process

### Validation
```bash
# Linting works
flake8 apps/backend
eslint apps/frontend/src

# Formatting works
black apps/backend
prettier apps/frontend/src

# Type checking works
mypy apps/backend

# Tests can run
pytest
jest
```

### Testing
- [ ] Black formatting works
- [ ] Flake8 detects errors
- [ ] MyPy type checking works
- [ ] ESLint catches issues
- [ ] Prettier formats code
- [ ] Pre-commit hooks run
- [ ] Pytest discovers tests
- [ ] Jest discovers tests
- [ ] Documentation is clear

### Related Issues
Enforces code quality for all development

### Estimated Effort
**1-2 days** — 300-500 lines (config + docs)

---

## Phase 0 Integration Points

### Dependencies Flow
```
PR-001 (Nx Setup)
    ↓
    ├→ PR-002 (Database) → PR-003 (Dev Env)
    ├→ PR-004 (CI/CD)
    ├→ PR-005 (Shared Libs)
    └→ PR-006 (Tooling)
    
After all PRs merged:
    ↓
One-command local dev: ./scripts/start-dev.sh
CI/CD pipeline active
Ready for Phase 1
```

### Blockers & Risks

| Risk | Probability | Mitigation |
|------|-------------|-----------|
| Nx + Python integration | Medium | Early spike, test both stacks |
| Docker/Docker Compose issues | Low | Test all services locally |
| CI/CD configuration | Medium | Start simple, iterate |
| Environment variable conflicts | Low | Validation script prevents |
| Database migration failures | Low | Test migrations thoroughly |

### Success Criteria for Phase 0

**All PRs merged and working:**
- ✅ Nx workspace initialized and working
- ✅ Docker services (Postgres, Redis) running
- ✅ Database schema created with migrations
- ✅ One command starts dev env: `./scripts/start-dev.sh`
- ✅ CI/CD pipeline active and passing
- ✅ Shared libraries importable
- ✅ Code quality tools configured
- ✅ All team members can run dev environment locally
- ✅ Documentation complete and clear

---

## PR Management for Phase 0

### Process
1. **Create feature branch** before starting work
   - Branch naming: `phase-0/{pr-number}-{description}`
   - Example: `phase-0/001-nx-monorepo`

2. **Create pr-work folder** with artifacts
   - Location: `pr-work/PHASE0-{number}-{feature}/`
   - Files: PR_DESCRIPTION.md, CHECKLIST.md, FINDINGS.md, ARTIFACTS/

3. **Commit with clear messages**
   - Format: `chore(phase-0): PR-001 description`
   - Example: `chore(phase-0): PR-001 Initialize Nx monorepo`

4. **Create PR using `gh`**
   ```bash
   gh pr create \
     --title "[Phase-0] PR-001 Nx Monorepo Initialization" \
     --body "$(cat pr-work/PHASE0-001-nx-monorepo/PR_DESCRIPTION.md)"
   ```

5. **Code review**
   - Minimum 1 reviewer
   - All CI checks must pass
   - Log findings in FINDINGS.md

6. **Merge when approved**
   ```bash
   gh pr merge {number} --squash --delete-branch
   ```

### Parallel Work
PRs can be worked on in parallel if they don't have circular dependencies:
- PR-001 (Nx) must complete first
- PR-002 (Database) and PR-004 (CI/CD) can work in parallel after PR-001
- PR-003, PR-005, PR-006 can work in parallel once PR-001 complete

**Recommended sequence for small team:**
1. Complete PR-001 (Nx Setup)
2. Start PR-002 and PR-004 in parallel
3. Complete PR-003 while waiting for PRs 2 & 4
4. Complete PR-005 and PR-006 in parallel

---

## Sign-Off Checklist

Phase 0 is complete when:

**Infrastructure:**
- [ ] Nx monorepo initialized and working
- [ ] Docker Compose stack functional (Postgres, Redis, LocalStack)
- [ ] Database schema created with all initial entities
- [ ] S3 simulation (LocalStack) working

**Development Environment:**
- [ ] .env configuration validated
- [ ] Development startup script works (`./scripts/start-dev.sh`)
- [ ] Database migration/seed scripts functional
- [ ] IDE configuration (.vscode) ready

**CI/CD & Quality:**
- [ ] GitHub Actions workflows defined and working
- [ ] All linting tools configured and passing
- [ ] Type checking (mypy, TypeScript) passing
- [ ] Branch protection rules active
- [ ] PR template configured

**Shared Code:**
- [ ] Backend shared library created and importable
- [ ] Frontend shared library created and importable
- [ ] No circular dependencies in Nx graph

**Documentation:**
- [ ] DEVELOPMENT.md complete
- [ ] CONTRIBUTING.md complete
- [ ] README updated with Phase 0 status
- [ ] All phase-0 PR artifacts archived

**Team Readiness:**
- [ ] All team members can run local dev env
- [ ] All team members understand dev workflow
- [ ] All team members can create/review PRs using `gh`
- [ ] No outstanding issues blocking Phase 1

**Ready to Begin Phase 1:**
- ✅ All 6 PRs merged to main
- ✅ No technical debt from Phase 0
- ✅ Team aligned on processes
- ✅ Infrastructure fully operational

---

## Timeline & Assignments

### Recommended Assignments (4-person team)

**Week 1:**
- **Developer 1:** PR-001 (Nx Monorepo) + PR-004 (CI/CD)
- **Developer 2:** PR-002 (Database) + PR-003 (Dev Env)
- **Developer 3:** PR-005 (Shared Libs) + support
- **Developer 4:** PR-006 (Tooling) + documentation

**Week 2:**
- All PRs merged and tested
- Address any blockers
- Team training on tools and processes
- Planning for Phase 1

### Daily Standup Template
```
What did I complete?
- PR status (in progress, needs review, merged)
- Blockers encountered

What am I working on today?
- Current PR tasks
- Support needed

Blockers or help needed?
- CI/CD issues
- Environment problems
- Questions on approach
```

---

## Next Document

Once Phase 0 is complete and all PRs are merged:
1. Create `docs/phase-1/PR_BREAKDOWN.md`
2. Begin Phase 1: Core Services (Auth → Profile → Chat)

**Estimated Phase 1 Start:** End of Week 2, 2026-07-26
