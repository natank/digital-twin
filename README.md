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
- **Frontend:** React 18+, TypeScript, Vite
- **AI/LLM:** Claude API
- **Notifications:** Pushover
- **Infrastructure:** Docker, Kubernetes, Nx Monorepo

## Quick Start

### Prerequisites
- Node.js 20+
- Python 3.11+
- Docker & Docker Compose
- `gh` CLI (GitHub command line)

### Local Development

```bash
# Clone and install
git clone https://github.com/yourusername/digital-twin.git
cd digital-twin
pnpm install
poetry install

# Start development stack
docker-compose up -d
pnpm nx run-many --target serve --projects=backend,frontend

# Access
Frontend: http://localhost:3000
API Docs: http://localhost:8000/docs
```

### Environment Setup

Copy and configure environment variables:
```bash
cp .env.example .env.local
# Edit .env.local with your credentials
```

## Project Structure

```
digital-twin/
├── apps/
│   ├── backend/          # FastAPI server
│   └── frontend/         # React application
├── libs/
│   ├── backend-shared/   # Python shared libraries
│   └── frontend-shared/  # React shared components
├── docs/                 # Documentation
├── e2e/                  # End-to-end tests
└── tools/                # Build tools & scripts
```

## Documentation

- [Operational Concept](./docs/OPERATIONAL_CONCEPT.md) — System overview and actors
- [Product Requirements](./docs/PRD.md) — Features and epics
- [Technical Design](./docs/TECHNICAL_DESIGN.md) — Architecture and implementation
- [Implementation Plan](./docs/IMPLEMENTATION_MASTER_PLAN.md) — Development roadmap

## Getting Started

### Phase 0: Foundation (Weeks 1-2)
- Setup Nx monorepo
- Initialize PostgreSQL & Redis
- Configure CI/CD pipeline
- Setup local development environment

### Phase 1: Core Services (Weeks 3-8)
- Auth Service (owner registration & login)
- Profile Service (CV upload & processing)
- Chat Service (visitor conversations)

### Phase 2: Supporting Services (Weeks 9-10)
- Notification Service (Pushover integration)
- Configuration Service (customize digital twin)

### Phase 3: Frontend (Weeks 11-14)
- Public pages & authentication UI
- Owner dashboard & profile management
- Chat interface & notifications

### Phase 4: Integration & Launch (Weeks 15-16)
- End-to-end testing
- Performance optimization
- Alpha user launch

See [Implementation Master Plan](./docs/IMPLEMENTATION_MASTER_PLAN.md) for details.

## Pull Request Workflow

All work is done via feature branches and pull requests.

```bash
# Start feature
pr_start e1 001 auth-registration

# Create PR
gh pr create --title "[E1] Add auth registration (#001)" \
             --body "$(cat pr-work/E1-001-auth-registration/PR_DESCRIPTION.md)"

# Address feedback
gh pr review {number} --approve

# Merge
gh pr merge {number} --squash --delete-branch
```

See [Pull Request Guidelines](./docs/IMPLEMENTATION_MASTER_PLAN.md#pull-request-management-guidelines) for complete workflow.

## Development Guidelines

- **Code Style:** Black (Python), Prettier (TypeScript)
- **Type Checking:** MyPy (Python), TypeScript (Frontend)
- **Testing:** pytest (backend), Jest (frontend) — Min 80% coverage
- **Commits:** Conventional commits with service prefix
- **Git:** Feature branches, squash commits on merge

## Available Commands

```bash
# Development
nx serve backend              # Start backend
nx serve frontend             # Start frontend
nx run-many --target serve    # Start all

# Testing
nx test backend              # Unit tests
nx test frontend
nx e2e e2e-tests            # End-to-end tests

# Linting & Formatting
nx lint backend
nx format:write              # Format all files

# Building
nx build backend             # Production build
nx build frontend
nx graph                      # Dependency graph
```

## Architecture

See [System Architecture](./docs/TECHNICAL_DESIGN.md#system-architecture) for detailed diagrams and design.

**High-Level Flow:**
```
Owner uploads CV → Profile summary generated → Digital twin ready
                                                        ↓
                                           Visitor asks question
                                                        ↓
                                           AI responds with context
                                                        ↓
                                           Owner gets notification
```

## Contributing

1. Create feature branch: `git checkout -b e1/001-auth-registration`
2. Implement feature with tests
3. Create PR: `gh pr create --title "..."`
4. Address review feedback
5. Merge when approved: `gh pr merge {number} --squash`

## Support & Issues

- Report bugs: `gh issue create --title "Bug: ..."`
- Ask questions: Open discussion
- View progress: `gh pr list --state open`

## License

[Add license here]

## Contact

For questions about the project, reach out to the team.

---

**Status:** MVP Development (Phase 0 - Foundation)  
**Last Updated:** 2026-07-19
