# Phase 2: Supporting Services - PR Breakdown

**Phase Duration:** Weeks 9–10 (10 working days)  
**Objective:** Complete the MVP backend with Notifications (E4 + Pushover E8) and Digital Twin Config (E5) as domain modules in the modular monolith  
**Success Criteria:** Owners receive in-app + Pushover alerts on chat activity; owners can customize system prompt, tone, topics; Chat uses owner config instead of only the built-in default  
**Depends on:** Phase 1 complete (Auth E1, Profile E2, Chat E3, Celery, CI green, merge policy)  
**Estimated start:** after Phase 1 Week 8 (~2026-09-06; adjust to actual velocity)

---

## Overview

Phase 2 is **backend-only** (same as Phase 1). React UI for notification center, Pushover setup screens, and config editors ships in **Phase 3**. This phase is API-first; OpenAPI remains the contract for frontend work.

Architecture reminder (TECHNICAL_DESIGN.md): one FastAPI app, domain modules under `apps/backend/src/`. “Service” means a **module**, not a separate deployable. Notifications reuse **Celery** (Phase 1 PR-006) for async delivery; Config is read synchronously by Chat on each reply.

```
Phase 2 Timeline:
Week 9  Notifications (E4) + Pushover (E8)
├── PR-001: Notifications domain shell + models + migration
├── PR-002: In-app notification API (list / read / delete / unread count)
├── PR-003: Pushover config storage + setup API (owner user key)
├── PR-004: Pushover client + Celery send task + retry
└── PR-005: Event wiring (chat/profile) + preferences + test notify

Week 10  Config (E5) + chat integration + polish
├── PR-006: Digital twin config models + owner-scoped CRUD
├── PR-007: System prompt edit, versions, preview
├── PR-008: Tone, response length, topic scope
├── PR-009: Wire Config into Chat (prompts + boundaries)
└── PR-010: Phase 2 integration tests & API polish

Buffer (end of Week 10 / Phase 3 planning):
├── Cross-module e2e smoke (chat → notify; config → chat reply)
├── Fix blockers from integration
└── Phase 3 PR breakdown (Frontend)
```

---

## PR Breakdown Summary

| PR #    | Title                                    | Epic     | Week | Est. lines | Priority | Status                                                            |
| ------- | ---------------------------------------- | -------- | ---- | ---------- | -------- | ----------------------------------------------------------------- |
| **001** | Notifications models + module shell      | E4       | 9    | 250–400    | P0       | ✅ Merged ([#26](https://github.com/natank/digital-twin/pull/26)) |
| **002** | In-app notification API                  | E4-S1    | 9    | 300–450    | P0       | ✅ Merged ([#26](https://github.com/natank/digital-twin/pull/26)) |
| **003** | Pushover config setup                    | E8-S1    | 9    | 300–450    | P0       | ✅ Merged ([#26](https://github.com/natank/digital-twin/pull/26)) |
| **004** | Pushover send + Celery retry             | E8-S2    | 9    | 350–550    | P0       | ✅ Merged ([#26](https://github.com/natank/digital-twin/pull/26)) |
| **005** | Event wiring + preferences + test notify | E4/E8    | 9    | 350–500    | P0       | ✅ Merged ([#26](https://github.com/natank/digital-twin/pull/26)) |
| **006** | Config models + owner CRUD               | E5       | 10   | 300–450    | P0       | ✅ Merged ([#28](https://github.com/natank/digital-twin/pull/28)) |
| **007** | System prompt + versions + preview       | E5-S1    | 10   | 350–500    | P0       | ✅ Merged ([#29](https://github.com/natank/digital-twin/pull/29)) |
| **008** | Tone, length, topic scope                | E5-S2/S3 | 10   | 250–400    | P1       | ✅ Merged ([#30](https://github.com/natank/digital-twin/pull/30)) |
| **009** | Chat integration with Config             | E5+E3    | 10   | 300–450    | P0       | ✅ Merged ([#31](https://github.com/natank/digital-twin/pull/31)) |
| **010** | Integration tests & API polish           | —        | 10   | 300–500    | P1       | ✅ Merged ([#32](https://github.com/natank/digital-twin/pull/32)) |

**Total scope (estimate):** ~3,000–4,700 lines across 10 PRs (application code + migrations + tests; lockfile churn excluded).

### What Phase 1 already provides (do not rebuild)

| Asset                                             | Location                                | Phase 2 usage                                             |
| ------------------------------------------------- | --------------------------------------- | --------------------------------------------------------- |
| Auth (`get_current_owner`, JWT sessions)          | `apps/backend/src/auth/`, `api/deps.py` | All owner-scoped notification/config routes               |
| Chat sessions + `message_processed` log hook      | `apps/backend/src/chat/service.py`      | Replace log with real event → notifications               |
| Default system prompt                             | `apps/backend/src/chat/prompts.py`      | Fallback when no owner config; seed for new configs       |
| Boundary heuristics                               | `apps/backend/src/chat/boundaries.py`   | Extend with owner `forbidden_topics` / `allowed_topics`   |
| Celery + Redis + eager tests                      | `apps/backend/src/worker/`              | Async Pushover delivery + retries                         |
| Profile summary pipeline                          | `apps/backend/src/profiles/`            | Optional `SUMMARY_READY` notification                     |
| Settings (`PUSHOVER_APP_TOKEN`, `ENCRYPTION_KEY`) | `apps/backend/src/settings.py`          | Expand; app token stays **platform-level** (PRD E8-S1)    |
| ApiResponse envelope + AppError hierarchy         | `libs/backend-shared`                   | Consistent errors for new modules                         |
| CI quality gates + merge policy                   | `.github/workflows/`, CONTRIBUTING.md   | **Green CI before merge**; `--admin` may skip review only |

### Explicitly deferred (not Phase 2)

| Item                                              | When                                                              |
| ------------------------------------------------- | ----------------------------------------------------------------- |
| React notification center / config UI             | Phase 3                                                           |
| Dashboard analytics charts (E4-S2)                | Phase 3 + optional Analytics epic (E7)                            |
| Full conversation browser UI + PDF export (E4-S3) | Phase 3 (thin owner conversation list API optional late Phase 2)  |
| Email / Slack notifications                       | Post-MVP (console email exists; not product channel yet)          |
| Do-not-disturb schedule UI (E8-S3 partial)        | Optional P2 in PR-005 if cheap; else Phase 3                      |
| Field-level KMS in production                     | Document Fernet/`ENCRYPTION_KEY` for MVP; cloud KMS Phase 4       |
| High-intent ML classifier                         | Lightweight heuristic only (keywords / boundary flags)            |
| Multi-tenant multi-app Pushover tokens per owner  | PRD: **one platform app token**; owner supplies **user key** only |

---

## Dependencies Flow

```
Phase 1 complete
    │
    ├─→ PR-001 (notification models)
    │       │
    │       ├─→ PR-002 (in-app API)
    │       │
    │       └─→ PR-003 (Pushover config) ──→ PR-004 (send + Celery)
    │                                              │
    │                                              └─→ PR-005 (events + preferences)
    │                                                         │
    ├─→ PR-006 (config models + CRUD) ──→ PR-007 (prompts/versions)
    │                                          │
    │                                          └─→ PR-008 (tone/topics)
    │                                                   │
    │                                                   └─→ PR-009 (chat uses config)
    │                                                              │
    └──────────────────────────────────────────────────────────────┴─→ PR-010 (integration)
```

**Hard rules:**

- No protected notification/config routes without Phase 1 auth (`get_current_owner`).
- Prefer **`/notifications/me/*`** and **`/config/me/*`** to avoid IDOR (same pattern as profiles).
- No live Pushover calls in CI — mock HTTP client / respx / injectable fake.
- Chat must keep working if Config row is missing (fallback to built-in default prompt).
- Notification delivery failures must **not** fail visitor chat responses (async + swallow).
- **Merge only when CI is green**; `--admin` may skip human review, never skip CI.

---

## PR-001: Notifications Models + Module Shell

### Objective

Introduce the notifications domain package, SQLAlchemy models, and Alembic migration without external HTTP calls.

### Scope

- [ ] Package `apps/backend/src/notifications/` with empty/status router
- [ ] Models (+ migration):
  - `Notification` — owner_id, type, title, message, data (JSON), priority, read, delivery_status, retry_count, pushover_receipt, created_at, sent_at
  - `PushoverConfig` — owner_id (unique), user_key ciphertext, device, sound, enabled, prefs JSON (optional defer detailed prefs to PR-005)
  - `NotificationPreference` — optional separate table **or** columns on `PushoverConfig` / JSON prefs; pick one approach and document
- [ ] Enums aligned with design:
  - Types: `conversation_started`, `message_received` (optional), `high_intent_detected`, `conversation_ended`, `profile_summary_ready`, `error_occurred`
  - Priority: -1 / 0 / 1 / 2 (Pushover mapping)
  - Delivery: `pending`, `sent`, `failed`, `skipped` (disabled / no config)
- [ ] Mount router under OpenAPI tag **Notifications**
- [ ] Settings placeholders: `pushover_app_token` (exists), document encryption requirement

### Suggested files

```
apps/backend/src/
├── notifications/
│   ├── __init__.py
│   ├── router.py          # /status only
│   ├── schemas.py         # enums + empty stubs
│   └── models usage via db/models.py
├── db/models.py           # Notification, PushoverConfig, …
migrations/versions/
└── e5f6a7b8c9d0_add_notifications.py
```

### Validation

```bash
pnpm nx run apps/backend:migrate
pnpm nx test apps/backend
curl -s localhost:8000/notifications/status
```

### Testing

- [ ] Models create/query on SQLite test session
- [ ] Migration upgrade/downgrade smoke (local Postgres)

### Estimated effort

**1–2 days** — 250–400 lines

---

## PR-002: In-App Notification API

### Objective

Owners can list, read, and delete in-app notifications (E4-S1 in-app path). Enables Phase 3 bell UI without push yet.

### Scope

- [ ] Endpoints (owner-scoped):
  - `GET /notifications/me` — paginated list (`limit`, `offset`, optional `unread_only`)
  - `GET /notifications/me/unread-count`
  - `POST /notifications/me/{id}/read` (or `PATCH`)
  - `POST /notifications/me/read-all` (optional, recommended)
  - `DELETE /notifications/me/{id}`
- [ ] Service: create_notification helper used later by events (no push yet)
- [ ] Authorization: only own rows
- [ ] Never return other owners’ data (IDOR tests)

### Acceptance mapping

| Criteria                    | Approach                                   |
| --------------------------- | ------------------------------------------ |
| In-app notification list    | Full                                       |
| Unread badge count          | Full                                       |
| Mark read                   | Full                                       |
| Email / Slack               | Deferred                                   |
| Dashboard conversation deep | Phase 3; `data` JSON may hold `session_id` |

### Testing

- [ ] Create via service → list returns item
- [ ] Other owner cannot read/delete
- [ ] Unauthenticated → 401

### Estimated effort

**1–2 days** — 300–450 lines

---

## PR-003: Pushover Config Setup

### Objective

Owners store Pushover **user key** and device/sound preferences (E8-S1). Platform **app token** remains `PUSHOVER_APP_TOKEN` in settings (PRD).

### Scope

- [ ] Encrypt `pushover_user_key` at rest (Fernet via `ENCRYPTION_KEY` or dedicated settings helper)
  - If `ENCRYPTION_KEY` empty in dev: document deterministic dev-only key **or** store plaintext with loud warning — prefer requiring key in `.env.example`
- [ ] Endpoints:
  - `GET /notifications/me/pushover` — status (enabled, device, sound, masked key suffix); never full secret
  - `PUT /notifications/me/pushover` — upsert user key + device + sound + enabled
  - `DELETE /notifications/me/pushover` — disable / remove config
- [ ] Validate user key format loosely (non-empty, length bounds)
- [ ] Invalid/missing app token → clear ExternalServiceError on later send, not on save (save is local)

### Testing

- [ ] Upsert + get masks key
- [ ] Encryption round-trip unit test
- [ ] Unauthenticated → 401

### Estimated effort

**1–2 days** — 300–450 lines

---

## PR-004: Pushover Client + Celery Send + Retry

### Objective

Deliver push notifications asynchronously with retries (E8-S2 core transport).

### Scope

- [ ] `notifications/pushover_client.py` — httpx client to `https://api.pushover.net/1/messages.json`
- [ ] Celery task `tasks.send_notification` (or `tasks.deliver_notification`):
  1. Load Notification + PushoverConfig
  2. If disabled / no config → `delivery_status=skipped`
  3. Call Pushover; store receipt; mark `sent` / `failed`
  4. Retry with backoff up to **3** attempts (PRD); exponential or Celery `autoretry_for`
- [ ] Map priority int to Pushover priority; emergency (2) needs retry/expire params per Pushover docs — implement minimally or document “emergency limited in MVP”
- [ ] Injectable client for tests (no live network)
- [ ] Settings: timeout, max retries

### Validation

```bash
# with CELERY_TASK_ALWAYS_EAGER=true and mock client
# create notification → task runs → status sent
```

### Testing

- [ ] Mock HTTP 200 → sent + receipt
- [ ] Mock HTTP 5xx → retry then failed
- [ ] Skipped when config missing/disabled

### Estimated effort

**2 days** — 350–550 lines

---

## PR-005: Event Wiring + Preferences + Test Notify

### Objective

Connect product events to notifications; owner preferences; test button (E4-S1, E8-S2/S3).

### Scope

- [ ] Event dispatcher / service API, e.g. `emit_notification_event(owner_id, type, title, message, data, priority)`
  - Creates `Notification` row
  - Enqueues Celery delivery
- [ ] Wire hooks:
  - Chat: on first visitor message in session → `conversation_started` (or every message → prefer **first message only** + optional high-intent)
  - Chat: boundary flag / keyword heuristic → `high_intent_detected` (lightweight)
  - Profile: summary generation completed → `profile_summary_ready` (optional but valuable)
  - Failures must not raise into chat request path (try/except + log)
- [ ] Preferences API:
  - `GET/PUT /notifications/me/preferences`
  - Per-type enable flags, global enabled, sound/device overrides if not only on PushoverConfig
- [ ] `POST /notifications/me/test` — sends test notification (requires configured user key)
- [ ] Replace chat `message_processed` log-only hook with dispatcher call

### Testing

- [ ] Chat message → notification row created (eager Celery)
- [ ] Preference off → skipped push but optional still store in-app (document choice; recommend **still store in-app**, skip push)
- [ ] Test endpoint with mock Pushover

### Estimated effort

**2 days** — 350–500 lines

---

## PR-006: Config Models + Owner CRUD

### Objective

Persist digital twin configuration per owner (E5 foundation). Prefer `/config/me` over raw `{owner_id}` for writes.

### Scope

- [ ] Models + migration:
  - `DigitalTwinConfig` — owner_id unique, system_prompt, tone, response_length, allowed_topics JSON, forbidden_topics JSON, brand_guidelines nullable
  - Auto-create default row on first access (from `chat.prompts.DEFAULT_SYSTEM_PROMPT` template filled with owner name later)
- [ ] Endpoints:
  - `GET /config/me`
  - `PUT /config/me` (partial fields)
- [ ] Defaults: tone=`professional`, response_length=`balanced`, topics empty lists = use built-in boundaries only
- [ ] Mount OpenAPI tag **Config**

### Testing

- [ ] GET auto-creates defaults
- [ ] PUT updates; other owner isolated
- [ ] 401 without auth

### Estimated effort

**1–2 days** — 300–450 lines

---

## PR-007: System Prompt + Versions + Preview

### Objective

E5-S1: edit prompt with version history and safe preview.

### Scope

- [ ] Model `PromptVersion` (config_id, system_prompt, version_number, created_at) **or** append-only history table
- [ ] Endpoints:
  - `GET /config/me/system-prompt`
  - `PUT /config/me/system-prompt` — validates non-empty, max length (e.g. 20K), stores version
  - `GET /config/me/system-prompt/versions`
  - `POST /config/me/system-prompt/restore/{version_number}` (optional, recommended)
  - `POST /config/me/system-prompt/preview` — body: `{ "system_prompt": "...", "sample_question": "..." }` returns mocked or real LLM sample; **mock in CI**
- [ ] Keep placeholders `{owner_name}`, `{profile_summary}` if using template mode; document whether owners edit full rendered prompt vs template
  - **Recommendation:** store **template** with allowed placeholders; render at chat time (matches Phase 1 prompts.py)

### Testing

- [ ] PUT creates version n+1
- [ ] List versions ordered
- [ ] Preview with mock LLM
- [ ] Reject empty / oversized prompt

### Estimated effort

**2 days** — 350–500 lines

---

## PR-008: Tone, Response Length, Topic Scope

### Objective

E5-S2 / E5-S3 configuration fields and validation.

### Scope

- [ ] Endpoints (can be sub-resources or fields on PUT `/config/me`):
  - `GET/PUT /config/me/tone` — enum: professional | casual | technical | friendly
  - `GET/PUT /config/me/topics` — allowed_topics[], forbidden_topics[]
  - Response length on main config or `/config/me/style`
- [ ] Validation: max N topics, string length limits, no empty strings
- [ ] Document how tone/length inject into system prompt (suffix rules in `prompts.py`)

### Testing

- [ ] Enum validation 422
- [ ] Topics round-trip
- [ ] Brand guidelines optional field

### Estimated effort

**1–2 days** — 250–400 lines

---

## PR-009: Wire Config into Chat

### Objective

Chat replies and boundaries respect owner configuration (E5 integration with E3).

### Scope

- [ ] On message generation:
  1. Load `DigitalTwinConfig` for session owner (or defaults)
  2. Render system prompt from template + profile_summary + tone/length/brand lines
  3. Pass forbidden/allowed topics into boundary check (extend `boundaries.py`)
- [ ] Fallback path if config missing (current Phase 1 behavior)
- [ ] Do **not** require notifications for chat success
- [ ] Optional: include config version id in log metadata for debugging

### Testing

- [ ] Custom prompt appears in LLM mock capture (assert system prompt contains unique marker)
- [ ] Forbidden topic → redirect without LLM
- [ ] Missing config → still replies with default

### Estimated effort

**1–2 days** — 300–450 lines

---

## PR-010: Phase 2 Integration Tests & API Polish

### Objective

Cross-module confidence and clean handoff to Phase 3 frontend.

### Scope

- [ ] E2E-style API tests (pytest, all mocked external IO):
  1. Register → login
  2. PUT config tone + custom prompt marker
  3. Create chat session → message → assert mock saw config
  4. Assert notification row created for conversation_started
  5. Mock Pushover delivery → notification `sent` (eager Celery)
  6. List `/notifications/me` shows item; mark read
- [ ] OpenAPI tags: Notifications, Config; examples for `/me` routes
- [ ] Update `docs/DEVELOPMENT.md` — Pushover mock, encryption key, config placeholders
- [ ] Update `.env.example` — `PUSHOVER_APP_TOKEN`, `ENCRYPTION_KEY`, any new vars
- [ ] Seed: sample `DigitalTwinConfig` + optional disabled Pushover for seed owner
- [ ] Extend `scripts/smoke-phase1.sh` or add `scripts/smoke-phase2.sh`
- [ ] Fix flaky tests if any (unique emails, Redis rate-limit isolation)

### Testing

- [ ] Integration suite green in CI
- [ ] No live Claude/Pushover in CI

### Estimated effort

**2 days** — 300–500 lines

---

## Module Layout Target (end of Phase 2)

```
apps/backend/src/
├── main.py
├── settings.py
├── api/
│   ├── deps.py
│   └── router.py                 # include notifications + config routers
├── auth/                         # Phase 1
├── profiles/                     # Phase 1
├── chat/
│   ├── router.py
│   ├── service.py                # emits notification events; loads config
│   ├── prompts.py                # render with tone/length/brand
│   └── boundaries.py             # owner topics
├── notifications/
│   ├── router.py
│   ├── schemas.py
│   ├── service.py                # create + list + prefs
│   ├── events.py                 # emit_notification_event
│   ├── pushover_client.py
│   └── encryption.py             # Fernet helpers (or shared crypto util)
├── config/                       # name: config package (avoid stdlib clash if needed: twin_config/)
│   ├── router.py
│   ├── schemas.py
│   ├── service.py
│   └── defaults.py
├── llm/claude.py
├── worker/tasks/
│   ├── cv.py
│   ├── ping.py
│   └── notifications.py          # deliver_notification
└── db/models.py                  # all models
```

> **Note:** Python’s stdlib has no top-level `config` package conflict, but if tooling complains, use `twin_config/` or `dtconfig/`. Prefer `config` for OpenAPI tag clarity unless imports get messy.

---

## Testing Strategy (Phase 2)

| Layer       | Tools                       | Notes                                    |
| ----------- | --------------------------- | ---------------------------------------- |
| Unit        | pytest                      | Encryption, prefs, prompt render, topics |
| API         | TestClient                  | Auth headers, pagination                 |
| Async tasks | Celery eager                | Notification delivery                    |
| Pushover    | Mock / respx / fake client  | Never live API in CI                     |
| LLM         | Existing chat/summary mocks | Config-aware system prompt assertions    |
| Redis       | Optional real / memory      | Only if new rate limits; prefer memory   |

**Coverage target:** ≥80% on new modules (review bar, not necessarily CI gate).

---

## Environment Variables (add during Phase 2)

```bash
# Pushover (platform app token — not per-owner)
PUSHOVER_APP_TOKEN=
PUSHOVER_API_URL=https://api.pushover.net/1/messages.json

# Encryption for Pushover user keys at rest
# Generate: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
ENCRYPTION_KEY=

# Optional tuning
NOTIFICATION_MAX_RETRIES=3
NOTIFICATION_RETRY_BACKOFF_SECONDS=30
CONFIG_SYSTEM_PROMPT_MAX_CHARS=20000
```

---

## PR Management (Phase 2)

### Branch naming

```text
phase-2/{pr-number}-{short-slug}
# examples:
phase-2/001-notifications-models
phase-2/004-pushover-send
phase-2/009-chat-config-integration
```

### Commit messages

```text
feat(notifications): in-app list and mark-read
feat(notifications): pushover client and celery delivery
feat(config): system prompt versions
feat(chat): load owner config into system prompt
test(notifications): mock pushover retries
docs(phase-2): note encryption key requirement
```

### PR titles

```text
[Phase-2] PR-002 In-app notification API
```

### pr-work artifacts (local, gitignored)

```text
pr-work/PHASE2-002-notifications-api/
  PR_DESCRIPTION.md
  ARTIFACTS/
```

### Review bar

- **CI green first** (`quality`, `test`, `build`, docker checks) — hard gate
- Migrations reversible
- No real secrets; Pushover/Claude mocked in tests
- OpenAPI updated for new routes
- Human review: **1 approval**, or **`--admin`** when solo (`--admin` does **not** waive green CI)
- Prefer `/me` routes; IDOR tests for owner-scoped resources

### Recommended sequencing (solo or small team)

1. **001 → 002** (in-app notifications usable)
2. **003 → 004 → 005** (push path + events)
3. **006 → 007 → 008 → 009** (config → chat)
4. **010** closes the phase

Parallelism: after **001**, Config track **006+** can proceed in parallel with **002–005**. **009** needs **006+** and benefits from **007/008**. **005** needs **002** and **004**.

---

## Risks & Mitigations

| Risk                                     | Likelihood | Mitigation                                                     |
| ---------------------------------------- | ---------- | -------------------------------------------------------------- |
| Live Pushover in CI / flaky network      | Medium     | Injectable mock; never call real API in tests                  |
| User key leakage in logs/API             | High       | Mask in GET; encrypt at rest; no keys in error details         |
| Chat latency if notify is sync           | High       | Celery only; never await Pushover in request path              |
| Config breaks chat prompts               | Medium     | Validation + fallback to DEFAULT_SYSTEM_PROMPT                 |
| Stdlib / package name `config` confusion | Low        | Clear package path; rename if tooling conflicts                |
| Scope creep (analytics, email, Slack)    | High       | Deferred table; reject in review                               |
| Emergency priority complexity            | Medium     | Document MVP limits; implement normal/high first               |
| ENCRYPTION_KEY missing in deploy         | Medium     | validate-env warning; refuse to store keys if unset in non-dev |

---

## Phase 2 Sign-Off Checklist

**Notifications (E4 / E8)**

- [ ] Owner lists in-app notifications; mark read / delete work
- [ ] Unread count endpoint correct
- [ ] Pushover user key can be saved (encrypted) and masked on read
- [ ] Test notification succeeds with mock (and optional live smoke)
- [ ] Chat first message creates notification without failing chat
- [ ] Celery delivery retries then marks failed
- [ ] Preferences can disable push while keeping in-app history

**Config (E5)**

- [ ] Owner GET/PUT config works; defaults auto-created
- [ ] System prompt update creates version history
- [ ] Tone / response length / topics persist
- [ ] Chat uses owner prompt + topics; fallback if no config
- [ ] Preview endpoint mocked in CI

**Engineering**

- [ ] All Phase 2 PRs merged; CI green on `main`
- [ ] Migrations Phase 1 head → Phase 2 head apply cleanly on empty DB
- [ ] DEVELOPMENT.md documents Pushover mock, encryption, config
- [ ] OpenAPI usable for Phase 3 notification center + settings UI
- [ ] No circular imports (chat → notifications → chat)

**Ready for Phase 3 when:**

- [ ] Auth + Profile + Chat + Notifications + Config demoable via curl
- [ ] Phase 3 PR breakdown drafted (`docs/phase-3/PR_BREAKDOWN.md`)

---

## Success Demo Script (end of Phase 2)

```bash
./scripts/start-dev.sh --seed
# API + Celery worker

TOKEN=$(curl -s -X POST localhost:8000/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"owner@example.com","password":"Owner123!"}' | jq -r .data.access_token)
OWNER=$(curl -s localhost:8000/auth/me -H "Authorization: Bearer $TOKEN" | jq -r .data.id)

# Config
curl -s -X PUT localhost:8000/config/me \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"tone":"friendly","response_length":"concise"}' | jq .

# Pushover setup (user key from https://pushover.net — optional live)
curl -s -X PUT localhost:8000/notifications/me/pushover \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"user_key":"…","enabled":true,"sound":"pushover"}' | jq .

curl -s -X POST localhost:8000/notifications/me/test \
  -H "Authorization: Bearer $TOKEN" | jq .

# Visitor chat → notification
SID=$(curl -s -X POST localhost:8000/chat/sessions \
  -H 'Content-Type: application/json' \
  -d "{\"owner_id\":\"$OWNER\"}" | jq -r .data.session_id)
curl -s -X POST "localhost:8000/chat/sessions/$SID/messages" \
  -H 'Content-Type: application/json' \
  -d '{"content":"What is your background?"}' | jq .

curl -s localhost:8000/notifications/me \
  -H "Authorization: Bearer $TOKEN" | jq .
```

---

## Related Documents

- [Phase 0 PR Breakdown](../phase-0/PR_BREAKDOWN.md) — foundation (complete)
- [Phase 1 PR Breakdown](../phase-1/PR_BREAKDOWN.md) — Auth / Profile / Chat (complete)
- [PRD](../PRD.md) — E4, E5, E8 acceptance criteria
- [Technical Design](../TECHNICAL_DESIGN.md) — notification & config models, Pushover client
- [Implementation Master Plan](../IMPLEMENTATION_MASTER_PLAN.md) — weeks 9–10 narrative
- [DEVELOPMENT.md](../DEVELOPMENT.md) — local tooling
- [CONTRIBUTING.md](../CONTRIBUTING.md) — PR process & merge policy

---

## Next Document

When Phase 2 sign-off is near complete:

1. Create `docs/phase-3/PR_BREAKDOWN.md` (Frontend: public + auth + dashboard + notification center + config UI)
2. Freeze OpenAPI for Phase 3 against Phase 2 head

**Estimated Phase 3 start:** after Week 10 (~2026-09-20), adjust to actual velocity.
