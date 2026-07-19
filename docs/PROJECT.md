# Digital Twin Project

## Overview
An AI-powered "digital twin" web product that represents a professional on their personal website. Visitors chat with an LLM-backed assistant that knows the owner's career background (extracted from an uploaded CV), answers professional questions, enforces topic boundaries, and notifies the owner of engagement via Pushover.

## Documentation Index
| Document | Purpose |
|----------|---------|
| [OPERATIONAL_CONCEPT.md](./OPERATIONAL_CONCEPT.md) | Actors, use cases, auth model, and digital twin AI behavior |
| [PRD.md](./PRD.md) | Product requirements: epics, user stories, acceptance criteria, roadmap |
| [TECHNICAL_DESIGN.md](./TECHNICAL_DESIGN.md) | Architecture, tech stack, database design, API specs, security |
| [IMPLEMENTATION_MASTER_PLAN.md](./IMPLEMENTATION_MASTER_PLAN.md) | 16-week phased implementation plan and PR workflow |
| [phase-0/](./phase-0/README.md) | Phase 0 (foundation) PR breakdown and quick reference |

## Project Structure
- **docs/** — Project specifications and documentation
- **apps/** — Application code (backend FastAPI, frontend React) once Phase 0 completes
- **libs/** — Shared backend/frontend libraries (Nx monorepo)

## Coding Workspace
Implementation workspace: `/Users/nati-home/Projects/digital-twin/`

## Architecture at a Glance
- **Backend:** Python 3.11+ / FastAPI modular monolith (single deployable, module-per-domain)
- **Frontend:** React 18+ / TypeScript / Vite, Tailwind CSS
- **Data:** PostgreSQL 14+, Redis 7+ (cache/sessions/rate limits), S3-compatible file storage
- **AI:** Claude API for profile summarization and chat responses
- **Notifications:** Pushover (MVP); email/Slack are post-MVP
- **Monorepo:** Nx with pnpm (frontend) and Poetry (backend)

## Getting Started
Local development setup lands in Phase 0 (see [phase-0/README.md](./phase-0/README.md)). Target: one-command startup via `./scripts/start-dev.sh`.
