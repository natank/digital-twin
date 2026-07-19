# Phase 1: Core Services - PR Breakdown

**Phase Duration:** Weeks 3–8 (30 working days)  
**Objective:** Ship the MVP backend for Auth (E1), Profile (E2), and Chat (E3) as domain modules inside the modular monolith  
**Success Criteria:** Owners can register/login; upload a CV and get an AI profile summary; visitors can chat with a twin that answers from profile context  
**Depends on:** Phase 0 complete (Nx, Postgres/Redis/LocalStack, migrations for Owners/Sessions/Profiles, CI, shared libs, tooling)  
**Estimated start:** 2026-07-26 (after Phase 0 Week 2 buffer)

---

## Overview

Phase 1 implements **backend-only** core services. The React UI ships in **Phase 3**; this phase is API-first (OpenAPI/Swagger is the contract).

Architecture reminder (TECHNICAL_DESIGN.md): one FastAPI app, domain modules under `apps/backend/src/`, shared utilities in `libs/backend-shared`. “Service” means a **module**, not a separate deployable.

```
Phase 1 Timeline:
Week 3–4  Auth (E1)
├── PR-001: API foundation (modules, middleware, errors, settings)
├── PR-002: Registration, login, JWT, GET /auth/me
├── PR-003: Logout, refresh, login rate limiting
├── PR-004: Email verification + password reset
└── PR-005: OAuth skeleton (Google / GitHub)

Week 5–6  Profile (E2) + async workers
├── PR-006: Celery + Redis worker infrastructure
├── PR-007: Profile CRUD API (owner-scoped)
├── PR-008: CV upload + S3/LocalStack storage
├── PR-009: CV text extraction + processing jobs
└── PR-010: LLM profile summary generation

Week 7–8  Chat (E3) + hardening
├── PR-011: Chat models + session lifecycle
├── PR-012: Messages + LLM response generation
├── PR-013: Streaming (SSE), boundaries, visitor rate limits
└── PR-014: Phase 1 integration tests & API polish

Buffer (end of Week 8 / start of Phase 2 planning):
├── Cross-module e2e smoke (auth → profile → chat)
├── Fix blockers from integration
└── Phase 2 PR breakdown (Notifications E4, Config E5)
```

---

## PR Breakdown Summary

| PR #    | Title                                | Epic | Week | Est. lines | Priority | Status                                                            |
| ------- | ------------------------------------ | ---- | ---- | ---------- | -------- | ----------------------------------------------------------------- |
| **001** | API foundation                       | —    | 3    | 250–400    | P0       | ✅ Merged ([#10](https://github.com/natank/digital-twin/pull/10)) |
| **002** | Auth: register / login / me          | E1   | 3    | 400–600    | P0       | ✅ Merged ([#11](https://github.com/natank/digital-twin/pull/11)) |
| **003** | Auth: session lifecycle + rate limit | E1   | 3–4  | 250–400    | P0       | ✅ Merged ([#12](https://github.com/natank/digital-twin/pull/12)) |
| **004** | Auth: verify email + password reset  | E1   | 4    | 350–500    | P1       | ✅ Merged ([#13](https://github.com/natank/digital-twin/pull/13)) |
| **005** | Auth: OAuth skeleton                 | E1   | 4    | 200–350    | P2       | ✅ Merged ([#14](https://github.com/natank/digital-twin/pull/14)) |
| **006** | Celery worker infrastructure         | —    | 5    | 250–400    | P0       | ✅ Merged ([#15](https://github.com/natank/digital-twin/pull/15)) |
| **007** | Profile CRUD API                     | E2   | 5    | 300–450    | P0       | ✅ Merged ([#16](https://github.com/natank/digital-twin/pull/16)) |
| **008** | CV upload + object storage           | E2   | 5    | 350–500    | P0       | ✅ Merged ([#17](https://github.com/natank/digital-twin/pull/17)) |
| **009** | CV extraction + job pipeline         | E2   | 5–6  | 400–600    | P0       | ✅ Merged ([#18](https://github.com/natank/digital-twin/pull/18)) |
| **010** | LLM profile summary                  | E2   | 6    | 400–600    | P0       | ✅ Merged ([#19](https://github.com/natank/digital-twin/pull/19)) |
| **011** | Chat models + sessions               | E3   | 7    | 350–500    | P0       | Not started                                                       |
| **012** | Chat messages + LLM replies          | E3   | 7–8  | 450–700    | P0       | Not started                                                       |
| **013** | Chat streaming + boundaries          | E3   | 8    | 350–550    | P1       | Not started                                                       |
| **014** | Integration tests & API polish       | —    | 8    | 300–500    | P1       | Not started                                                       |

**Total scope (estimate):** ~4,500–7,000 lines across 14 PRs (application code + migrations + tests; lockfile churn excluded).

### What Phase 0 already provides (do not rebuild)

| Asset                                     | Location                                          | Phase 1 usage                                            |
| ----------------------------------------- | ------------------------------------------------- | -------------------------------------------------------- |
| `Owner`, `OwnerSession`, `Profile` models | `apps/backend/src/db/models.py`                   | Extend with new tables; auth/profile reuse existing rows |
| Alembic + migrate/seed Nx targets         | `apps/backend`                                    | New revisions only                                       |
| DB session dependency                     | `apps/backend/src/db/session.py`                  | Inject into routes                                       |
| Settings (root `.env.local`)              | `apps/backend/src/settings.py`                    | Expand fields (JWT, S3, Claude, email, OAuth)            |
| Exceptions, schemas, utils, logging       | `libs/backend-shared`                             | Import; add auth helpers where shared                    |
| Password policy helper                    | `backend_shared.utils.validate_password_strength` | Registration / reset                                     |
| LocalStack S3, Redis, Postgres            | `docker-compose.yml`                              | Storage + Celery broker + DB                             |
| CI quality gates                          | `.github/workflows/ci.yml`                        | All PRs must stay green                                  |

### Explicitly deferred (not Phase 1)

| Item                                      | When                                                            |
| ----------------------------------------- | --------------------------------------------------------------- |
| React auth/profile/chat UI                | Phase 3                                                         |
| LinkedIn integration (E2-S5)              | Post-MVP / later epic (P2)                                      |
| Config Service custom system prompts (E5) | Phase 2 — Chat uses a **built-in default** prompt               |
| Notification Service / Pushover (E4)      | Phase 2 — Chat may emit in-process events/hooks only            |
| Analytics (E7)                            | Optional later                                                  |
| WebSocket chat                            | Optional; **SSE preferred** in PR-013 for MVP                   |
| Virus scan on CV upload                   | Stub/log only; real scanning later                              |
| Production email provider                 | Interface + console/dev backend; SendGrid/SES Phase 4           |
| Password history (last 5)                 | Nice-to-have; simple single-hash invalidation is enough for MVP |

---

## Dependencies Flow

```
PR-001 (API foundation)
    │
    ├─→ PR-002 (Auth register/login) ──→ PR-003 (logout/refresh/rate limit)
    │                                      │
    │                                      ├─→ PR-004 (verify + reset)
    │                                      └─→ PR-005 (OAuth skeleton)
    │
    ├─→ PR-006 (Celery) ──┐
    │                     │
    └─→ PR-007 (Profile CRUD) ──→ PR-008 (CV upload)
                                    │
                                    └─→ PR-009 (extract jobs) ──→ PR-010 (LLM summary)
                                                                    │
PR-002+ required for protected routes ──────────────────────────────┤
                                                                    ▼
                                                          PR-011 (chat models)
                                                                    │
                                                          PR-012 (messages + LLM)
                                                                    │
                                                          PR-013 (stream + boundaries)
                                                                    │
                                                          PR-014 (integration)
```

**Hard rules:**

- No protected Profile/Chat routes before **PR-002** lands (`get_current_owner`).
- No CV async processing before **PR-006**.
- No Chat LLM replies without a usable profile summary path (**PR-010** or a test fixture that seeds summary JSON).
- **PR-005** (OAuth) must not block Profile/Chat — skeleton only.

---

## PR-001: API Foundation

### Objective

Wire the modular monolith so domain modules can mount routers with consistent errors, settings, CORS, and auth dependency hooks.

### Scope

- [ ] Package layout under `apps/backend/src/`:
  - `api/` or module packages: `auth/`, `profiles/`, `chat/` (empty routers OK)
  - `core/` or `middleware/`: exception handlers, CORS, request ID logging
- [ ] Map `backend_shared` exceptions → HTTP status + `ApiResponse` envelope
- [ ] Expand `Settings` for Phase 1 placeholders (JWT, CORS origins, Claude, S3, email, OAuth) without implementing features
- [ ] `get_current_owner` dependency **stub** that 401s until PR-002 fills it
- [ ] Mount routers on `FastAPI` app; keep `/health`
- [ ] OpenAPI tags: Auth, Profiles, Chat

### Suggested files

```
apps/backend/src/
├── main.py                    # include routers, middleware
├── settings.py                # expanded fields
├── api/
│   ├── __init__.py
│   ├── deps.py                # get_db re-export, get_current_owner stub
│   └── router.py              # top-level APIRouter
├── auth/                      # package shell
├── profiles/
└── chat/
```

### Validation

```bash
pnpm nx serve apps/backend
curl -s localhost:8000/health
curl -s localhost:8000/openapi.json | head
pnpm nx test apps/backend
```

### Testing

- [ ] Exception handler returns envelope for `ValidationError` / `NotFoundError`
- [ ] CORS preflight OK for configured origin
- [ ] `/health` unchanged

### Estimated effort

**1–2 days** — 250–400 lines

---

## PR-002: Auth — Registration, Login, JWT, Me

### Objective

Owners can register with email/password, log in, and fetch their identity. Implements E1-S1 (core) + E1-S2 (core, no OAuth yet).

### Scope

- [ ] Password hashing: **bcrypt** (or argon2 — pick one; document in PR notes)
- [ ] JWT access tokens (secret + expiry from settings; align with `JWT_SECRET` / `JWT_EXPIRY` already in `.env.example`)
- [ ] Persist `OwnerSession` on login (token hash or jti stored — never store raw JWT if avoidable; document choice)
- [ ] Endpoints:
  - `POST /auth/register`
  - `POST /auth/login`
  - `GET /auth/me` (protected)
- [ ] Use `validate_password_strength` from `backend_shared`
- [ ] Duplicate email → `ConflictError` (409)
- [ ] Generic invalid-login message (no user enumeration)
- [ ] Implement real `get_current_owner` dependency
- [ ] Seed script optionally uses real password hash for `owner@example.com` (update seed)

### Acceptance mapping

| Criteria                             | Approach                                                                                           |
| ------------------------------------ | -------------------------------------------------------------------------------------------------- |
| Email/password register              | Full                                                                                               |
| Password policy                      | Full via shared utils                                                                              |
| Duplicate email                      | Full                                                                                               |
| Email verification before activation | **Partial:** `email_verified=False` on register; enforce in PR-004 or allow login in dev with flag |
| Welcome email                        | Defer send to PR-004 interface (log only OK here)                                                  |
| OAuth register                       | PR-005                                                                                             |

### Validation

```bash
# register → login → me
curl -X POST localhost:8000/auth/register -H 'Content-Type: application/json' -d '{...}'
curl -X POST localhost:8000/auth/login -H 'Content-Type: application/json' -d '{...}'
curl localhost:8000/auth/me -H "Authorization: Bearer $TOKEN"
```

### Testing

- [ ] Unit: hash/verify, JWT encode/decode
- [ ] API: register happy path, weak password, duplicate email
- [ ] API: login success/fail, me with/without token

### Estimated effort

**2–3 days** — 400–600 lines

---

## PR-003: Auth — Logout, Refresh, Rate Limiting

### Objective

Complete session lifecycle and brute-force protection (E1-S2 remainder).

### Scope

- [ ] `POST /auth/logout` — invalidate current session (DB row + client discards token)
- [ ] `POST /auth/refresh-token` — rotate access token; bound to valid session
- [ ] Login rate limit: **5 attempts / 15 min** per email (and optionally per IP)
  - Redis counters preferred; in-memory only if Redis down + document failover
- [ ] Optional “remember me” longer expiry (7d) if cheap; else document as Phase 3 UI concern
- [ ] CORS already from PR-001; confirm credentials headers if cookie-based (prefer **Bearer** for API)

### Validation

```bash
# 6 failed logins → 429
# logout → me returns 401
# refresh extends session
```

### Testing

- [ ] Rate limit integration test (Redis or fake)
- [ ] Logout invalidates session
- [ ] Refresh rejects expired/revoked sessions

### Estimated effort

**1–2 days** — 250–400 lines

---

## PR-004: Auth — Email Verification & Password Reset

### Objective

E1-S1 verification + E1-S3 recovery, with a pluggable email backend.

### Scope

- [ ] Email abstraction: `EmailSender` protocol + `ConsoleEmailSender` (dev logs body)
- [ ] Email verification token (store hash, TTL e.g. 24h)
  - `POST /auth/verify-email` or `GET /auth/verify-email?token=`
  - Resend endpoint optional
- [ ] Password reset:
  - `POST /auth/forgot-password` (always 202/generic message)
  - `POST /auth/reset-password` (token + new password)
  - Token TTL 1 hour (PRD)
- [ ] Invalidate sessions on password reset
- [ ] Settings: `EMAIL_FROM`, provider keys placeholders
- [ ] **Skip** password history of last 5 for MVP (note deviation)

### Models / migration

- Prefer columns on `owners` or small `owner_tokens` table (`type`, `token_hash`, `expires_at`) — choose one approach and migrate via Alembic autogenerate

### Testing

- [ ] Verify flow activates account
- [ ] Reset flow changes password; old login fails
- [ ] Expired/invalid tokens rejected
- [ ] Console email captured in tests via fake sender

### Estimated effort

**2 days** — 350–500 lines

---

## PR-005: Auth — OAuth Skeleton (Google / GitHub)

### Objective

Scaffold OAuth without blocking MVP email/password path (E1-S1/S2 OAuth AC partial).

### Scope

- [ ] Routes:
  - `POST /auth/oauth/google` (or start + callback pair)
  - `POST /auth/oauth/github`
- [ ] Config: client id/secret in settings (empty → 503 “not configured”)
- [ ] Create/link `Owner` with `oauth_provider` + `oauth_id`
- [ ] Issue same JWT/session as password login
- [ ] No production redirect UX required; document callback URLs for later frontend
- [ ] Integration tests with **mocked** provider token exchange

### Out of scope

- Full browser OAuth dance UI (Phase 3)
- Account linking when email already exists (document as follow-up)

### Estimated effort

**1–2 days** — 200–350 lines

---

## PR-006: Celery Worker Infrastructure

### Objective

Async task runner on Redis for CV processing (and later notifications).

### Scope

- [ ] Add Celery app (`apps/backend/src/worker/` or `tasks/`)
- [ ] Broker/backend = `REDIS_URL`
- [ ] Example health task `tasks.ping`
- [ ] Nx targets or scripts: `worker` (celery worker), document in DEVELOPMENT.md
- [ ] Optional: docker-compose `worker` service (can stay host-run for dev like API)
- [ ] Poetry deps: `celery`, keep redis client
- [ ] Logging integration with `backend_shared.logging`

### Validation

```bash
# terminal A
pnpm nx serve apps/backend
# terminal B
poetry run celery -A src.worker.celery_app worker -l INFO
# enqueue ping from a small script or pytest
```

### Testing

- [ ] Unit: task registration
- [ ] Optional: eager mode `CELERY_TASK_ALWAYS_EAGER=true` in pytest

### Estimated effort

**1–2 days** — 250–400 lines

---

## PR-007: Profile CRUD API

### Objective

Authenticated owners can read/update their profile (E1-S4 + E2 foundation). Models already exist from Phase 0.

### Scope

- [ ] Endpoints (owner-scoped; prefer `/profiles/me` to avoid IDOR):
  - `GET /profiles/me`
  - `PUT /profiles/me` (bio, headline, skills, experience_years)
  - Optional: `GET /profiles/{owner_id}` **public** limited fields for chat later
- [ ] Auto-create empty `Profile` on first access if missing (register may also create one)
- [ ] Pydantic schemas; never return `cv_extracted_text` unless needed (size/PII)
- [ ] Authorization: only self for write

### Testing

- [ ] CRUD happy path
- [ ] Other owner cannot update (if numeric id routes exist)
- [ ] Unauthenticated → 401

### Estimated effort

**1–2 days** — 300–450 lines

---

## PR-008: CV Upload + Object Storage

### Objective

Owners upload PDF/DOCX to S3-compatible storage (LocalStack in dev) — E2-S1.

### Scope

- [ ] `POST /profiles/me/cv` (multipart) — alias PRD `POST /profiles/cv/upload`
- [ ] Validate: content type, extension, max **10MB**
- [ ] Store under `s3://{bucket}/cv-uploads/{owner_id}/{uuid}-{filename}`
- [ ] Set `Profile.cv_file_path`; clear previous object optional
- [ ] `GET /profiles/me/cv` — presigned URL or stream (document choice)
- [ ] boto3/aioboto3 client with `AWS_ENDPOINT_URL` for LocalStack
- [ ] Encryption-at-rest: rely on bucket defaults in dev; document KMS for prod
- [ ] Virus scan: stub hook (log “skipped in dev”)

### Testing

- [ ] Reject oversize / bad type
- [ ] Upload hits LocalStack (or moto)
- [ ] Path persisted on profile

### Estimated effort

**2 days** — 350–500 lines

---

## PR-009: CV Text Extraction + Processing Jobs

### Objective

Async extract text from uploaded CVs — E2-S2.

### Scope

- [ ] Model `CVProcessingJob` (+ Alembic migration)
- [ ] `POST /profiles/me/process-cv` enqueues Celery task
- [ ] Task: download from S3 → extract (pypdf / python-docx) → clean text → update job + `Profile.cv_extracted_text`
- [ ] Job statuses: pending / processing / completed / failed
- [ ] `GET /profiles/me/cv/jobs/{job_id}` status endpoint
- [ ] Failures set `error_message`; owner-visible safe message

### Testing

- [ ] PDF and DOCX fixtures
- [ ] Failed extraction marks job failed
- [ ] Eager Celery in unit tests

### Estimated effort

**2–3 days** — 400–600 lines

---

## PR-010: LLM Profile Summary Generation

### Objective

Generate structured profile summary via Claude — E2-S3 + E2-S4 API side.

### Scope

- [ ] Claude client wrapper (httpx/anthropic SDK); `CLAUDE_API_KEY` from settings
- [ ] Extend processing pipeline or separate task step: extracted text → JSON summary
- [ ] Store `profile_summary`, `skills`, `experience_years` when present in model output
- [ ] Endpoints:
  - `GET /profiles/me/summary`
  - `PUT /profiles/me/summary` (owner edit)
  - Regenerate: re-run process or `POST /profiles/me/summary/regenerate`
- [ ] Mock LLM in tests (no live API in CI)
- [ ] Prompt + schema documented in module docstring
- [ ] Timeout / failure handling with owner-visible error

### Testing

- [ ] Mocked LLM success updates profile
- [ ] Owner PUT summary validation
- [ ] Missing CV text → 400

### Estimated effort

**2–3 days** — 400–600 lines

---

## PR-011: Chat Models + Session Lifecycle

### Objective

Visitors get anonymous chat sessions bound to an owner twin — E3-S4 foundation.

### Scope

- [ ] Models + migration:
  - `ChatSession` (owner_id, public session key, visitor_ip hash optional, expires_at)
  - `Message` (session_id, sender enum, content, tokens_used)
  - Optional `ConversationContext` (can wait for PR-013 if size is high)
- [ ] Endpoints:
  - `POST /chat/sessions` body: `{ "owner_id": "..." }` (or owner slug later)
  - `GET /chat/sessions/{session_id}`
  - `DELETE /chat/sessions/{session_id}` (visitor end)
- [ ] Expiry: **30 minutes** inactivity (PRD); update `expires_at` on activity
- [ ] No auth for visitor session create; owner must exist and be active
- [ ] Public read of twin metadata minimal (headline only) optional

### Testing

- [ ] Session create/get/delete
- [ ] Expired session rejected
- [ ] Unknown owner → 404

### Estimated effort

**2 days** — 350–500 lines

---

## PR-012: Chat Messages + LLM Responses

### Objective

Visitors send messages; twin replies from profile context — E3-S2 core (non-streaming first).

### Scope

- [ ] `POST /chat/sessions/{session_id}/messages` — visitor message
- [ ] `GET /chat/sessions/{session_id}/messages` — history
- [ ] Validate max **10K** chars
- [ ] Load owner `profile_summary` + default system prompt (Config Service later)
- [ ] Call Claude (reuse client from PR-010); mock in tests
- [ ] Persist visitor + AI messages; track `tokens_used` when available
- [ ] Synchronous response JSON for MVP path (`{ "reply": "..." }`)
- [ ] Error fallback message if LLM fails
- [ ] Hook point for notifications (no-op / log event `message_processed`)

### Testing

- [ ] Message persistence order
- [ ] Mocked LLM reply stored
- [ ] Reject empty / oversize messages
- [ ] Expired session cannot post

### Estimated effort

**2–3 days** — 450–700 lines

---

## PR-013: Streaming, Boundaries, Visitor Rate Limits

### Objective

Better UX and safety — E3-S2 streaming, E3-S3 boundaries, abuse controls.

### Scope

- [ ] SSE endpoint: `GET /chat/sse/{session_id}/stream` or stream on POST via `text/event-stream`
- [ ] Boundary enforcement: system prompt rules + optional lightweight classifier/heuristic
  - Off-topic → polite redirect; still persist messages
  - Flag conversation on repeated violations (`ConversationContext.flagged` if model exists)
- [ ] Visitor rate limit: **50 req/hour/session** (PRD) via Redis
- [ ] Document WebSocket as future alternative (not required)

### Testing

- [ ] SSE emits chunks then completes (TestClient/httpx stream)
- [ ] Boundary cases return redirect-style content
- [ ] Rate limit returns 429

### Estimated effort

**2 days** — 350–550 lines

---

## PR-014: Phase 1 Integration Tests & API Polish

### Objective

Cross-module confidence and clean handoff to Phase 2/3.

### Scope

- [ ] E2E-style API tests (pytest):
  1. Register → login
  2. Upload CV fixture → process (eager Celery) → summary present
  3. Create chat session as visitor → message → AI reply
- [ ] OpenAPI review: consistent tags, examples, error schemas
- [ ] Update `docs/DEVELOPMENT.md` with worker + auth + LocalStack S3 usage
- [ ] Update `.env.example` with any new vars
- [ ] Seed data: known password, sample summary for chat demos
- [ ] Fix flaky tests / coverage gaps on critical paths
- [ ] Optional: `scripts/` smoke script for local demo

### Testing

- [ ] Integration suite green in CI (mock LLM; LocalStack or moto for S3)
- [ ] No live Claude/Pushover calls in CI

### Estimated effort

**2 days** — 300–500 lines

---

## Module Layout Target (end of Phase 1)

```
apps/backend/src/
├── main.py
├── settings.py
├── api/
│   ├── deps.py              # get_db, get_current_owner
│   └── router.py
├── auth/
│   ├── router.py
│   ├── schemas.py
│   ├── service.py
│   ├── security.py          # jwt, password, rate limit
│   └── oauth.py
├── profiles/
│   ├── router.py
│   ├── schemas.py
│   ├── service.py
│   ├── storage.py           # S3
│   └── extraction.py
├── chat/
│   ├── router.py
│   ├── schemas.py
│   ├── service.py
│   ├── prompts.py
│   └── boundaries.py
├── llm/
│   └── claude.py            # shared Claude client
├── worker/
│   ├── celery_app.py
│   └── tasks/
│       ├── cv.py
│       └── ping.py
├── email/
│   └── sender.py
└── db/
    ├── base.py
    ├── models.py            # all SQLAlchemy models
    └── session.py
```

---

## Testing Strategy (Phase 1)

| Layer       | Tools                      | Notes                                   |
| ----------- | -------------------------- | --------------------------------------- |
| Unit        | pytest                     | Services, security, prompts, extraction |
| API         | httpx + FastAPI TestClient | Auth headers, multipart upload          |
| Async tasks | Celery eager mode          | Default in tests                        |
| LLM         | Mock / respx               | Never call real API in CI               |
| S3          | LocalStack or moto         | Prefer moto for unit speed              |
| Redis       | fakeredis or real compose  | Rate limits                             |

**Coverage target:** keep Phase 0 standard — aim ≥80% on new modules; enforce in review not necessarily CI gate yet.

---

## Environment Variables (add during Phase 1)

Extend `.env.example` as PRs land (do not invent secrets in git):

```bash
# Auth
JWT_SECRET=...
JWT_EXPIRY=86400
AUTH_LOGIN_MAX_ATTEMPTS=5
AUTH_LOGIN_LOCKOUT_SECONDS=900

# OAuth (optional until PR-005)
GOOGLE_OAUTH_CLIENT_ID=
GOOGLE_OAUTH_CLIENT_SECRET=
GITHUB_OAUTH_CLIENT_ID=
GITHUB_OAUTH_CLIENT_SECRET=

# Email (console in dev)
EMAIL_BACKEND=console
EMAIL_FROM=noreply@localhost

# LLM
CLAUDE_API_KEY=
CLAUDE_MODEL=claude-sonnet-4-20250514   # pin when implementing

# S3 (LocalStack)
S3_BUCKET=digital-twin-dev
AWS_ENDPOINT_URL=http://localhost:4566
AWS_ACCESS_KEY_ID=test
AWS_SECRET_ACCESS_KEY=test
AWS_DEFAULT_REGION=us-east-1

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/1
# Tests:
# CELERY_TASK_ALWAYS_EAGER=true
```

---

## PR Management (Phase 1)

### Branch naming

```text
phase-1/{pr-number}-{short-slug}
# examples:
phase-1/001-api-foundation
phase-1/002-auth-register-login
phase-1/010-profile-llm-summary
```

### Commit messages

```text
feat(auth): register and login with JWT
feat(profiles): upload CV to LocalStack S3
feat(chat): persist messages and generate replies
test(auth): rate limit login attempts
docs(phase-1): note OAuth skeleton limits
```

### PR titles

```text
[Phase-1] PR-002 Auth register/login/me
```

### pr-work artifacts (local, gitignored)

```text
pr-work/PHASE1-002-auth-register-login/
  PR_DESCRIPTION.md
  ARTIFACTS/
```

### Review bar

- CI green (`quality`, `test`, `build`, docker checks)
- Migrations reversible (`upgrade` / `downgrade` smoke)
- No real secrets; LLM/S3 mocked in unit tests
- OpenAPI updated for new routes
- 1 approval (or `--admin` if solo, same as late Phase 0)

### Recommended sequencing (solo or small team)

1. **001 → 002 → 003** (auth usable)
2. **004** and **005** can trail; **006** can start after 001
3. **007 → 008 → 009 → 010** (profile pipeline)
4. **011 → 012 → 013** (chat)
5. **014** closes the phase

Parallelism: after **002**, Profile work needs auth; Celery **006** can proceed in parallel with **003–005**.

---

## Risks & Mitigations

| Risk                                   | Likelihood | Mitigation                                                 |
| -------------------------------------- | ---------- | ---------------------------------------------------------- |
| Claude API cost/flakes in dev          | Medium     | Mock default; live key only opt-in                         |
| LocalStack S3 quirks                   | Medium     | moto in unit tests; one manual LocalStack check per PR-008 |
| JWT/session design churn               | Medium     | Decide token storage in PR-002 notes; avoid dual systems   |
| CV extraction quality variance         | High       | Store raw text; allow owner summary edit (PR-010)          |
| Scope creep (LinkedIn, WS, virus scan) | High       | Deferred list above; reject in review                      |
| Celery + FastAPI dual process DX       | Medium     | Document in DEVELOPMENT.md; eager mode for tests           |
| IDOR on profile/chat                   | Medium     | Prefer `/me` routes; explicit owner checks in tests        |

---

## Phase 1 Sign-Off Checklist

**Auth (E1)**

- [ ] Register + login + `/auth/me` work against live Postgres
- [ ] Logout / refresh / rate limit verified
- [ ] Password reset path works with console email
- [ ] OAuth skeleton responds predictably when unconfigured
- [ ] Passwords hashed; JWT secret not default in non-dev envs (docs warn)

**Profile (E2)**

- [ ] Owner can CRUD profile fields
- [ ] CV upload to S3/LocalStack succeeds
- [ ] Processing job extracts text (PDF + DOCX fixtures)
- [ ] LLM summary written (mocked in CI, optional live smoke)
- [ ] Owner can edit summary

**Chat (E3)**

- [ ] Visitor creates session for an owner
- [ ] Messages persist; AI reply generated from profile context
- [ ] Streaming or documented sync fallback works
- [ ] Boundaries + rate limits enforced
- [ ] Default system prompt used (Config Service not required)

**Engineering**

- [ ] All Phase 1 PRs merged; CI green on `main`
- [ ] Migrations from Phase 0 → Phase 1 head apply cleanly on empty DB
- [ ] DEVELOPMENT.md documents worker, auth headers, S3, LLM mocks
- [ ] No circular imports in module graph
- [ ] OpenAPI usable for Phase 3 frontend work

**Ready for Phase 2 when:**

- [ ] Auth + Profile + Chat APIs demoable via curl/httpie or Bruno collection
- [ ] Notification and Config PR breakdown drafted (`docs/phase-2/PR_BREAKDOWN.md`)

---

## Success Demo Script (end of Phase 1)

```bash
./scripts/start-dev.sh --seed
# terminal: API + Celery worker

# 1) Auth
TOKEN=$(curl -s -X POST localhost:8000/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"owner@example.com","password":"..."}' | jq -r .data.access_token)

# 2) Profile + CV
curl -X POST localhost:8000/profiles/me/cv \
  -H "Authorization: Bearer $TOKEN" \
  -F file=@./fixtures/sample.pdf
curl -X POST localhost:8000/profiles/me/process-cv \
  -H "Authorization: Bearer $TOKEN"
curl localhost:8000/profiles/me/summary -H "Authorization: Bearer $TOKEN"

# 3) Chat (visitor)
SID=$(curl -s -X POST localhost:8000/chat/sessions \
  -H 'Content-Type: application/json' \
  -d '{"owner_id":"..."}' | jq -r .data.session_id)
curl -X POST localhost:8000/chat/sessions/$SID/messages \
  -H 'Content-Type: application/json' \
  -d '{"content":"What is your background?"}'
```

---

## Related Documents

- [Phase 0 PR Breakdown](../phase-0/PR_BREAKDOWN.md) — foundation (complete)
- [PRD](../PRD.md) — E1 / E2 / E3 acceptance criteria
- [Technical Design](../TECHNICAL_DESIGN.md) — endpoints, models, prompts
- [Implementation Master Plan](../IMPLEMENTATION_MASTER_PLAN.md) — weeks 3–8 narrative
- [DEVELOPMENT.md](../DEVELOPMENT.md) — local tooling
- [CONTRIBUTING.md](../CONTRIBUTING.md) — PR process

---

## Next Document

When Phase 1 sign-off is near complete:

1. Create `docs/phase-2/PR_BREAKDOWN.md` (Notifications E4, Config E5)
2. Keep Phase 3 (Frontend) planned against the OpenAPI frozen at Phase 1 end

**Estimated Phase 2 start:** after Week 8 (~2026-09-06), adjust to actual velocity.
