## finding description

login fails

## applicable documents

1. technical design: `docs/TECHNICAL_DESIGN.md`
2. implementation master plan: `docs/IMPLEMENTATION_MASTER_PLAN.md`
3. screen capture: `docs/production-findings/finding-3/finding-3.png`

## next tasks

see screem capture - ref 3
find root cause and fix on a bug branch

## root cause

The screen capture shows the `/auth/login` request (preflight + fetch) failing
with `net::ERR_CONNECTION_REFUSED`, initiated from `client.ts:62`. The frontend
runs on `:4200` but nothing is listening on `:8000`, where the backend API
(`uvicorn src.main:app`) serves. In other words the browser could not reach the
API at all — this was **not** a credential/auth failure.

Operationally this happens because `scripts/start-dev.sh` brings up infra only
(Postgres/Redis/LocalStack); the API is a separate manual step
(`pnpm nx serve apps/backend`). When it isn't running, login can never reach the
server.

Underlying code defect that made this confusing: when `fetch()` fails at the
network level it rejects with a `TypeError` ("Failed to fetch"), not an
`ApiClientError`. `LoginPage` only special-cases `ApiClientError`, so it fell
back to the generic **"Login failed. Please try again."** — identical to the
message shown for genuinely wrong credentials. The user reasonably read a
server-down condition as a login problem.

## resolution

Branch: `fix/login-network-error-message`

- `apps/frontend/src/lib/api/client.ts` — wrap the `fetch` call; on a network
  failure throw a typed `ApiClientError` with code `NETWORK_ERROR` and a clear
  message ("Cannot reach the server at <url>…"). `LoginPage` already renders
  `ApiClientError.message`, so the UI now distinguishes "server unreachable"
  from "invalid credentials".
- `apps/frontend/src/lib/api/client.spec.ts` — added a test reproducing the
  finding (fetch rejects with `TypeError`) and asserting the `NETWORK_ERROR`
  envelope.

To actually log in locally, start the backend: `pnpm nx serve apps/backend`
(API on http://localhost:8000).
