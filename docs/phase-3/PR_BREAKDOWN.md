# Phase 3: Frontend - PR Breakdown

**Phase Duration:** Weeks 11–14 (20 working days)  
**Objective:** Ship a working React SPA so owners can register/login, manage their twin, and visitors can chat from a public page  
**Success Criteria:** Homepage + auth flows work; owners reach a protected dashboard; visitors can open a chat session and exchange messages against a live backend  
**Depends on:** Phase 2 complete (Auth, Profile, Chat, Notifications, Config APIs green on `main`)  
**Estimated start:** after Phase 2 Week 10 (adjust to actual velocity)

---

## Overview

Phase 3 is **frontend-first**. Backend contracts already exist under OpenAPI (`/auth`, `/profiles`, `/chat`, `/notifications`, `/config`). New backend work is limited to thin gaps (e.g. owner conversation list if missing for the conversation browser).

Architecture reminder (TECHNICAL_DESIGN.md): Vite + React SPA in `apps/frontend`, shared UI in `libs/frontend-shared`, API base URL via `VITE_API_URL` (default `http://localhost:8000`). CORS already allows `http://localhost:4200`.

```
Phase 3 Timeline:
Week 11  Core pages (public + auth)
├── PR-001: App shell — Router, layouts, API client, auth context
├── PR-002: Auth pages — login, register, reset, verify
├── PR-003: Public pages — home, nav, about
├── PR-004: Public chat widget (visitor session + messages)
└── PR-005: Dashboard shell + protected routes + Week 11 tests

Week 12  Profile management
├── PR-006: Dashboard layout polish (sidebar, user menu)
├── PR-007: Profile view + edit fields
├── PR-008: CV upload UI + job status polling
├── PR-009: Profile summary review / edit
└── PR-010: Account settings (password, basic prefs)

Week 13  Chat interface polish
├── PR-011: Message UI components (bubbles, input, timestamps)
├── PR-012: SSE streaming client for replies
├── PR-013: Typing/loading states + error recovery
└── PR-014: Responsive layout + a11y pass for chat

Week 14  Dashboard, notifications, config UI
├── PR-015: Notification center (list, unread badge, mark read)
├── PR-016: Pushover setup page
├── PR-017: Conversation browser (list + detail; thin API if needed)
├── PR-018: Digital twin config UI (prompt, tone, topics)
└── PR-019: Phase 3 polish, smoke script, docs handoff

Buffer (end of Week 14 / Phase 4 planning):
├── Cross-stack smoke (register → CV → chat → notify)
├── Fix blockers from UI integration
└── Phase 4 PR breakdown (integration & launch)
```

---

## PR Breakdown Summary

| PR #    | Title                                          | Epic     | Week | Est. lines | Priority | Status                                                            |
| ------- | ---------------------------------------------- | -------- | ---- | ---------- | -------- | ----------------------------------------------------------------- |
| **001** | App shell: router, API client, auth context    | FE-core  | 11   | 400–600    | P0       | ✅ Merged ([#35](https://github.com/natank/digital-twin/pull/35)) |
| **002** | Auth pages (login / register / reset / verify) | FE-auth  | 11   | 400–600    | P0       | ✅ Merged ([#36](https://github.com/natank/digital-twin/pull/36)) |
| **003** | Public homepage, navigation, about             | FE-pub   | 11   | 300–450    | P0       | ✅ Merged ([#37](https://github.com/natank/digital-twin/pull/37)) |
| **004** | Public chat widget                             | FE-chat  | 11   | 400–600    | P0       | ✅ Merged ([#38](https://github.com/natank/digital-twin/pull/38)) |
| **005** | Dashboard shell + protected routes + tests     | FE-dash  | 11   | 350–500    | P0       | ✅ Merged ([#38](https://github.com/natank/digital-twin/pull/38)) |
| **006** | Dashboard layout polish (sidebar, user menu)   | FE-dash  | 12   | 300–450    | P0       | Not started                                                       |
| **007** | Profile view + basic edit                      | FE-prof  | 12   | 350–500    | P0       | Not started                                                       |
| **008** | CV upload UI + processing status               | FE-prof  | 12   | 400–600    | P0       | Not started                                                       |
| **009** | Profile summary review / edit                  | FE-prof  | 12   | 300–450    | P0       | Not started                                                       |
| **010** | Account settings                               | FE-set   | 12   | 250–400    | P1       | Not started                                                       |
| **011** | Chat message UI components                     | FE-chat  | 13   | 350–500    | P0       | Not started                                                       |
| **012** | SSE streaming for chat replies                 | FE-chat  | 13   | 350–550    | P0       | Not started                                                       |
| **013** | Chat loading, errors, reconnection             | FE-chat  | 13   | 250–400    | P1       | Not started                                                       |
| **014** | Chat responsive + accessibility                | FE-chat  | 13   | 250–400    | P1       | Not started                                                       |
| **015** | Notification center UI                         | FE-notif | 14   | 350–500    | P0       | Not started                                                       |
| **016** | Pushover setup UI                              | FE-notif | 14   | 250–400    | P0       | Not started                                                       |
| **017** | Conversation browser (+ thin owner API)        | FE-conv  | 14   | 400–650    | P0       | Not started                                                       |
| **018** | Digital twin config UI                         | FE-cfg   | 14   | 350–550    | P0       | Not started                                                       |
| **019** | Phase 3 polish, smoke, docs                    | —        | 14   | 300–500    | P1       | Not started                                                       |

**Total scope (estimate):** ~6,300–9,700 lines across 19 PRs (TSX/CSS/tests; lockfile churn excluded).

### What Phase 0–2 already provide (do not rebuild)

| Asset                                             | Location                         | Phase 3 usage                                    |
| ------------------------------------------------- | -------------------------------- | ------------------------------------------------ |
| React + Vite app scaffold                         | `apps/frontend`                  | Replace Nx welcome with real routes              |
| Shared `Button`, `Input`, validators              | `libs/frontend-shared`           | Compose auth/profile forms                       |
| Shared TS types (`ApiResponse`, `Owner`, …)       | `libs/frontend-shared/src/types` | Extend for wire `snake_case` as needed           |
| Auth API (register/login/me/logout/refresh/reset) | `POST/GET /auth/*`               | Auth pages + context                             |
| Profile + CV upload + summary                     | `/profiles/me/*`                 | Week 12                                          |
| Chat sessions + messages + SSE                    | `/chat/sessions/*`               | Public widget + Week 13 polish                   |
| Notifications + Pushover                          | `/notifications/me/*`            | Week 14                                          |
| Digital twin config                               | `/config/me/*`                   | Week 14                                          |
| CORS + `VITE_API_URL`                             | settings + `.env.example`        | SPA → API                                        |
| CI quality/test/build/docker gates                | `.github/workflows/`             | **Green CI before merge**; admin may skip review |

### Explicitly deferred (not Phase 3)

| Item                                | When                                  |
| ----------------------------------- | ------------------------------------- |
| Production email provider UI polish | Phase 4 / ops                         |
| Full analytics charts (E7)          | Optional late Week 14 or post-MVP     |
| LinkedIn import UI                  | Post-MVP                              |
| Dark mode theme system              | Optional polish; not required for MVP |
| Native mobile apps                  | Out of scope                          |
| Multi-language i18n                 | Post-MVP                              |
| Conversation PDF export polish      | Minimal export OK; heavy layout later |

---

## Dependencies Flow

```
Phase 2 complete (API on main)
    │
    ├─→ PR-001 (shell: router + api + auth context)
    │       │
    │       ├─→ PR-002 (auth pages)
    │       │
    │       ├─→ PR-003 (public pages)
    │       │       │
    │       │       └─→ PR-004 (chat widget)
    │       │
    │       └─→ PR-005 (dashboard shell + tests)
    │               │
    │               ├─→ PR-006 … PR-010 (Week 12 profile)
    │               │
    │               ├─→ PR-011 … PR-014 (Week 13 chat polish)
    │               │
    │               └─→ PR-015 … PR-019 (Week 14 dashboard features)
```

**Hard rules:**

- JWT access tokens stored in `localStorage` (or sessionStorage) for MVP; never log tokens.
- All owner routes behind a `ProtectedRoute` that calls `/auth/me` (or uses cached owner) and redirects to `/login`.
- API client always sends `Authorization: Bearer <token>` when present; maps envelope errors to typed `ApiError`.
- Wire JSON is **snake_case** (backend Pydantic); map at the client boundary or type API models as snake_case.
- No live Claude/Pushover required in frontend unit tests — mock `fetch` / API module.
- Public chat must work **without** auth; dashboard must **require** auth.
- Demo twin owner id via `VITE_DEMO_OWNER_ID` (document seed owner) until a public twin directory exists.
- **Merge only when CI is green**; `--admin` may skip human review, never skip CI.
- Prefer separate PRs per row above; stack on `main` after each green merge.

---

## Week 11 Detail

## PR-001: App Shell — Router, Layouts, API Client, Auth Context

### Objective

Replace the Nx welcome page with a routable SPA foundation every later PR builds on.

### Scope

- [ ] Add `react-router-dom` dependency
- [ ] `BrowserRouter` + top-level routes skeleton (public layout, auth layout, dashboard layout placeholders)
- [ ] `src/lib/api/client.ts` — `apiFetch` with base URL, JSON, envelope unwrap, `ApiClientError`
- [ ] `src/lib/auth/storage.ts` — get/set/clear access token
- [ ] `src/lib/auth/AuthContext.tsx` — `AuthProvider`, `useAuth` (`owner`, `token`, `login`, `logout`, `refreshMe`, `isLoading`)
- [ ] Vite env: `ImportMetaEnv` for `VITE_API_URL`, `VITE_DEMO_OWNER_ID`, `VITE_DEBUG`
- [ ] Minimal global layout chrome (header slot, main, footer slot)
- [ ] Remove / gate `nx-welcome` so App is route-driven
- [ ] Unit tests: API client error handling (mock fetch); auth storage

### Out of scope

- Full auth forms (PR-002)
- Real dashboard pages (PR-005+)
- Chat UI (PR-004)

### Testing

- [ ] Vitest: client throws on `status: error`
- [ ] Vitest: token round-trip in storage
- [ ] `pnpm nx test frontend` / typecheck / lint green

### Estimated effort

**1 day** — 400–600 lines

---

## PR-002: Auth Pages

### Objective

Owners can register and log in through the SPA.

### Scope

- [ ] `/login` — email/password form → `POST /auth/login` → store token → navigate dashboard
- [ ] `/register` — first/last/email/password → `POST /auth/register` → auto-login or redirect login
- [ ] `/forgot-password` — `POST /auth/forgot-password` (success message always)
- [ ] `/reset-password?token=` — `POST /auth/reset-password`
- [ ] `/verify-email?token=` — `POST /auth/verify-email`
- [ ] Client-side validation via `frontend-shared` (`isValidEmail`, `validatePasswordStrength`)
- [ ] OAuth buttons as **disabled skeleton** (Google/GitHub) with “coming soon”
- [ ] Error display from API envelope

### Out of scope

- Real OAuth redirect flow
- Profile onboarding wizard

### Testing

- [ ] Form validation tests (weak password, invalid email)
- [ ] Login success navigates when API mocked
- [ ] Register surfaces API error message

### Estimated effort

**1–1.5 days** — 400–600 lines

---

## PR-003: Public Homepage, Navigation, About

### Objective

Marketing-facing shell for visitors and unauthenticated owners.

### Scope

- [ ] Public layout with top nav: Logo, Home, About, Chat, Login, Register
- [ ] `/` homepage — hero, value props, CTA to chat + register
- [ ] `/about` — short product description
- [ ] Responsive header (basic mobile wrap or hamburger)
- [ ] Footer with links
- [ ] Auth-aware nav: when logged in show Dashboard + Logout instead of Login/Register

### Out of scope

- Polished design system / brand illustrations
- Blog / marketing CMS

### Testing

- [ ] Home and about render key copy
- [ ] Nav links present

### Estimated effort

**0.5–1 day** — 300–450 lines

---

## PR-004: Public Chat Widget

### Objective

Visitors can chat with a digital twin without logging in.

### Scope

- [ ] `/chat` page (and optional floating entry from home)
- [ ] Create session: `POST /chat/sessions` with `owner_id` from `VITE_DEMO_OWNER_ID` (or query `?owner=`)
- [ ] Message list + input; `POST /chat/sessions/{id}/messages`
- [ ] Display visitor + AI messages; show boundary redirect notice if flagged
- [ ] Session expiry / error messaging
- [ ] Non-streaming replies first (SSE in Week 13 PR-012)
- [ ] Loading state while waiting for reply
- [ ] Document `VITE_DEMO_OWNER_ID` in `.env.example` + DEVELOPMENT.md

### Out of scope

- SSE streaming
- Owner conversation browser
- File attachments

### Testing

- [ ] Mocked session create + message exchange renders reply
- [ ] Missing demo owner id shows setup hint

### Estimated effort

**1–1.5 days** — 400–600 lines

---

## PR-005: Dashboard Shell + Protected Routes + Week 11 Tests

### Objective

Authenticated owners land on a dashboard shell; Week 11 flows are covered by tests and smoke notes.

### Scope

- [ ] `ProtectedRoute` — redirect unauthenticated users to `/login?next=`
- [ ] `/dashboard` shell — welcome, owner name/email, links to future Profile / Settings / Notifications
- [ ] Logout control (calls `POST /auth/logout` when possible + clear token)
- [ ] Route table complete for Week 11 paths
- [ ] Integration-style frontend tests: register/login flow with mocked API; protected route redirect
- [ ] Update `docs/DEVELOPMENT.md` frontend section (routes, env vars, how to run with backend)
- [ ] Optional: `scripts/smoke-phase3-ui.md` or short shell notes (curl not required)

### Out of scope

- Profile/CV pages (Week 12)
- Notification center (Week 14)

### Testing

- [ ] Protected route redirects when no token
- [ ] Dashboard renders owner from context
- [ ] Full Week 11 Vitest suite green in CI

### Estimated effort

**1 day** — 350–500 lines

---

## Week 12–14 Summaries

### PR-006 … PR-010 (Week 12 — Profile)

Dashboard sidebar; profile GET/PUT; CV multipart upload + poll job; summary display/edit; account settings stubs.

### PR-011 … PR-014 (Week 13 — Chat polish)

Extract reusable chat components; `EventSource`/fetch-stream for SSE; typing indicators; mobile + WCAG basics (labels, focus, contrast).

### PR-015 … PR-019 (Week 14 — Ops UI)

Notification list/badge; Pushover key form; owner conversation list (add thin backend list endpoint if still missing); config editor for system prompt / tone / topics; Phase 3 smoke + status docs.

---

## Frontend Layout Target (end of Phase 3)

```
apps/frontend/src/
├── main.tsx
├── styles.css
├── vite-env.d.ts
├── app/
│   ├── app.tsx                 # Router + providers
│   ├── routes.tsx              # route table
│   └── providers.tsx
├── lib/
│   ├── api/
│   │   ├── client.ts
│   │   ├── auth.ts
│   │   ├── chat.ts
│   │   ├── profiles.ts
│   │   ├── notifications.ts
│   │   └── config.ts
│   └── auth/
│       ├── AuthContext.tsx
│       ├── storage.ts
│       └── ProtectedRoute.tsx
├── layouts/
│   ├── PublicLayout.tsx
│   ├── AuthLayout.tsx
│   └── DashboardLayout.tsx
├── pages/
│   ├── HomePage.tsx
│   ├── AboutPage.tsx
│   ├── LoginPage.tsx
│   ├── RegisterPage.tsx
│   ├── ForgotPasswordPage.tsx
│   ├── ResetPasswordPage.tsx
│   ├── VerifyEmailPage.tsx
│   ├── ChatPage.tsx
│   ├── DashboardPage.tsx
│   ├── profile/…
│   ├── settings/…
│   ├── notifications/…
│   └── config/…
├── components/
│   ├── NavBar.tsx
│   ├── chat/
│   └── notifications/
└── styles/                     # layout CSS modules
```

---

## Testing Strategy

| Layer        | Tool                        | Focus                                            |
| ------------ | --------------------------- | ------------------------------------------------ |
| Unit         | Vitest + Testing Library    | Forms, validators, API client, auth context      |
| Component    | Vitest + Testing Library    | Chat bubbles, nav, protected route               |
| Integration  | Vitest + mocked fetch       | Login → dashboard; chat session → message        |
| Manual smoke | Browser + local API         | Seed owner, demo chat, register happy path       |
| CI           | Existing quality/test/build | ESLint, tsc, vitest, vite build, docker-frontend |

**Never** call live Claude or Pushover from frontend tests.

---

## Environment Variables (frontend)

| Variable             | Purpose                            | Default / example           |
| -------------------- | ---------------------------------- | --------------------------- |
| `VITE_API_URL`       | Backend base URL                   | `http://localhost:8000`     |
| `VITE_DEMO_OWNER_ID` | Public chat twin owner UUID (seed) | _(empty — show setup hint)_ |
| `VITE_DEBUG`         | Verbose client logging             | `true` in local             |

Document in `.env.example` and `docs/DEVELOPMENT.md` as PRs land.

---

## Merge Policy

Same as Phase 1–2 retrospective:

1. **Required CI green** on PR head: `quality`, `test`, `build`, `docker-backend`, `docker-frontend`
2. **Admin may skip review** (`gh pr merge --admin`) for solo velocity
3. **Admin must not merge red CI**
4. Prefer **squash** merges; delete branch after merge
5. Keep PRs focused; one row of the summary table per PR when practical

---

## Success Criteria (Phase 3 exit)

- [ ] Visitor opens `/chat`, messages the demo twin, sees AI reply (with backend + mocks/Claude key as configured)
- [ ] Owner registers, logs in, lands on `/dashboard`
- [ ] Owner uploads CV and edits summary (Week 12)
- [ ] Owner sees notifications and can configure Pushover + twin config (Week 14)
- [ ] Frontend CI green on `main`; DEVELOPMENT.md documents SPA routes and env
- [ ] No secrets committed; tokens not logged

---

## References

- [IMPLEMENTATION_MASTER_PLAN.md](../IMPLEMENTATION_MASTER_PLAN.md) — Phase 3 weeks 11–14
- [TECHNICAL_DESIGN.md](../TECHNICAL_DESIGN.md) — SPA + API contract
- [PRD.md](../PRD.md) — owner/visitor journeys
- [phase-2/PR_BREAKDOWN.md](../phase-2/PR_BREAKDOWN.md) — backend APIs consumed here
- [CONTRIBUTING.md](../CONTRIBUTING.md) — merge policy
- [DEVELOPMENT.md](../DEVELOPMENT.md) — local runbook

```

```
