## finding description

UX issue: the chat widget gives no visual indication when it's running against the
seeded/sample demo owner rather than a specific, explicitly-chosen owner. This is
misleading — the header renders like a real profile ("Sample · Software Engineer"),
so a visitor (or the owner themself, previewing their twin) has no way to tell
they're not talking to the intended twin. This is the same confusion that caused
finding-4: after uploading a resume, the dashboard's "Public chat" link landed on
the seeded demo profile with no indication anything was off.

## applicable documents

1. technical design: `docs/TECHNICAL_DESIGN.md`
2. related finding: `docs/production-findings/finding-4/finding-4.md`
3. relevant code:
   - `apps/frontend/src/components/chat/ChatWidget.tsx`
   - `apps/frontend/src/pages/ChatPage.tsx`
   - `apps/frontend/src/pages/DashboardPage.tsx`
   - `apps/backend/scripts/seed_data.py`

## current behavior

`ChatWidget` resolves an owner id in this order (`ChatWidget.tsx:24`):

```ts
const resolvedOwner = (ownerId || getDemoOwnerId()).trim();
```

- `ownerId` prop — passed down from `ChatPage`'s `?owner=` query param, or explicitly
  by callers like the dashboard link fixed in finding-4.
- `getDemoOwnerId()` — falls back to `VITE_DEMO_OWNER_ID`, an env var pointing at
  the seeded "Sample Owner" account.

Once resolved, the widget just starts a session and renders the twin's real
name/headline in the header (`ChatWidget.tsx:69`, `202-207`):

```ts
setTitle(headline ? `${name} · ${headline}` : `Chat with ${name}`);
```

There is **no distinction** in the rendered UI between:
- an owner id explicitly supplied via `?owner=` / a real dashboard link, vs.
- the `VITE_DEMO_OWNER_ID` fallback silently kicking in.

Both look identical: a normal-looking chat header with a name and headline. Only
a developer inspecting the URL or env config would know which mode is active.

## why this is misleading

1. **Owners previewing their own twin** land here after finding-4's fix (`/chat?owner={id}`),
   but if that link is ever broken, misconfigured, or opened without the query param
   (e.g. a bookmarked `/chat`, a shared link stripped of query params, an env var
   unset in a new environment), the widget silently falls back to the demo profile
   with zero warning. The owner has no way to know they're not looking at their own
   twin's answers — exactly what produced finding-4's confusing bug report.
2. **Real visitors** hitting a misconfigured deployment (`VITE_DEMO_OWNER_ID` set but
   no explicit `?owner=` in a shared link) would unknowingly chat with a sample
   profile and could form a wrong impression of the actual owner's skills/experience.
3. There's no way to switch owners from within the widget — recovering from a wrong
   context requires manually editing the URL.

## next tasks

Suggest a UX refactor (no fix required by this finding alone — file for follow-up):

1. **Explicit "sample mode" indicator.** When `resolvedOwner` came from
   `getDemoOwnerId()` (no explicit `ownerId` prop / no `?owner=` in the URL), render
   a visible, non-dismissible banner or header badge, e.g.:

   > ⚠️ **Sample twin** — this is a demo profile, not a live owner. [Learn how to preview your own twin →]

   This should be a distinct visual treatment (banner color, icon) from the normal
   `notice`/`error` banners already in the widget, so it can't be missed or confused
   with a transient message.

2. **Surface which mode is active in component state**, not just inferred from props.
   Concretely: have `ChatWidget` track `ownerSource: 'explicit' | 'demo-fallback'`
   instead of only holding the resolved id, so the render logic (and tests) can
   assert on it directly rather than re-deriving it from props/env each time.

3. **In-widget owner switcher.** Add a small affordance (e.g. a "Switch owner"
   link/input next to the status line) that lets a developer/tester paste an owner
   id and re-open a session against it without leaving the page or editing the URL
   — useful in dev/staging, and doubles as a discoverable way to notice you're in
   sample mode (since "switch owner" only makes sense if you're not already viewing
   a specific one).

4. **Owner-side: make the dashboard preview link self-verifying.** Since finding-4
   already makes `DashboardPage` pass `?owner={owner.id}` explicitly, consider having
   `ChatWidget` assert/display the owner id it actually started a session for
   (e.g. small muted text under the header: `Previewing as {owner_id}`) so a future
   regression (link losing its query param again) is visible immediately in the UI
   instead of silently reproducing finding-4.

## root cause

n/a — this is a UX/design gap, not a functional defect. The demo fallback itself is
reasonable (lets `/chat` work out of the box in dev without requiring a query param),
but the lack of any visual signal when that fallback is active is what makes it
misleading.

## resolution (branch `feat/chat-sample-mode-indicator`)

Implemented all four suggestions in `ChatWidget.tsx`:

- Added `ownerSource: 'explicit' | 'demo-fallback'` component state, set from whether
  an `ownerId` prop was supplied (vs. the `VITE_DEMO_OWNER_ID` fallback), instead of
  re-deriving it from props on every render.
- When `ownerSource === 'demo-fallback'`, a distinct, non-dismissible "Sample twin"
  banner renders above the conversation (`styles.sampleBanner`), visually separate
  from the existing transient `notice`/`error` banners. Shown to every visitor
  (real or previewing owner) regardless of mode, since it protects anyone from
  unknowingly talking to the seed profile.
- Added a `preview` prop (wired from a new `?preview=1` query param, set only by the
  dashboard's "Public chat" link) that gates just the raw owner-id text. A bare
  `Previewing as {uuid}` string reads as leaked debug output to a real visitor with
  no context for what it means, so it's shown only in preview mode — meaningful for
  an owner confirming their own twin loaded, hidden otherwise.
- The owner switcher is collapsed by default behind a small "Switch owner" text
  link next to the status line — a persistent label+input+button row competed
  with the actual chat for attention and read as cluttered. Clicking it toggles
  an inline input + "Switch" button (and the link becomes "Cancel"); the input
  auto-focuses on open, and Escape collapses it again. Submitting it resets
  session/conversation state, re-starts a session against the pasted owner id,
  marks `ownerSource` as `'explicit'`, and collapses the switcher.
- Added `forwardRef` to the shared `Input` component (`libs/frontend-shared`) so
  it can be focused programmatically — needed to auto-focus the owner field when
  the switcher opens.
- Fixed a layout bug in the (then always-visible) owner-switcher row — label
  butting against the input with no breathing room — by giving the `Input`
  wrapper `min-width: 0` / full-width input and proper row spacing/gap; this
  styling carries over to the now-collapsible version.

Verified via component tests in `ChatWidget.spec.tsx` (sample banner shown to all
visitors regardless of preview mode; raw owner id hidden for regular visitors and
shown only with `preview`; switcher collapsed by default and toggled open/closed
via the link; switching owner clears the sample banner, starts a new session, and
re-collapses the switcher) plus `Input.spec.tsx` in `frontend-shared`, and `tsc`
typecheck. No live browser/E2E verification was done in this pass (no browser
automation tool available in the dev environment).
