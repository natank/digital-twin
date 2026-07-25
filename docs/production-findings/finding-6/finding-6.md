## finding description

The sidebar notification indicator (unread count badge) doesn't update when a
notification's status changes to read. After marking one notification — or all
notifications — as read on the Notifications page, the sidebar badge keeps showing
the old (higher) unread count instead of reflecting the change immediately.

## applicable documents

1. technical design: `docs/TECHNICAL_DESIGN.md`
2. relevant code:
   - `apps/frontend/src/components/notifications/UnreadBadge.tsx`
   - `apps/frontend/src/pages/dashboard/NotificationsPage.tsx`
   - `apps/frontend/src/layouts/DashboardLayout.tsx`
   - `apps/frontend/src/lib/api/notifications.ts`

## current behavior

`DashboardLayout.tsx` renders `UnreadBadge` persistently in the sidebar nav next to
the "Notifications" link (`DashboardLayout.tsx:41`). `NotificationsPage` renders
separately inside the routed `<Outlet />` (`DashboardLayout.tsx:106`). These are two
independent components, each with their own local state and their own fetch of the
unread count — there is no shared state or event between them:

- `UnreadBadge` (`UnreadBadge.tsx:10-33`) keeps its own `count` state, fetched via
  `getUnreadCount()` on mount and then re-polled every 30 seconds
  (`window.setInterval(() => void refresh(), 30_000)`), and never in response to any
  other action in the app.
- `NotificationsPage` (`NotificationsPage.tsx:32-51`) keeps its own separate `unread`
  state, fetched via `listNotifications()`. When the user marks one notification read
  (`onMarkRead`, lines 57-68) or all read (`onMarkAll`, lines 70-81), the page calls
  `load()` again afterward, which correctly updates _its own_ `unread` state and list
  — but nothing tells `UnreadBadge` that anything changed.

Result: after marking notifications read, `NotificationsPage`'s inline unread count
("X unread." / "All caught up.") updates instantly, while the sidebar `UnreadBadge`
keeps showing the previous, now-stale count until its own 30-second poll happens to
fire next — or indefinitely if the owner navigates away from the notifications page
before that poll runs.

## why this is misleading

- The two indicators visibly disagree for up to 30 seconds after a read action:
  the page says "All caught up." while the sidebar still shows a badge with a
  non-zero count.
- An owner has no reliable signal that marking something read actually worked,
  since the most persistently visible indicator (the sidebar badge) doesn't move.
- If the owner navigates elsewhere in the dashboard right after marking notifications
  read, the stale badge can persist for the rest of that 30s window (or longer, since
  the interval resets per-mount / isn't tied to the read action at all) — it always
  needs a fresh 30s tick from whenever `UnreadBadge` last polled, not from the read
  action itself.

## next tasks

find root cause and fix on a bug branch. Likely direction: share the unread count
across `UnreadBadge` and `NotificationsPage` (e.g. lift it into a shared context/hook,
or have the mark-read/mark-all-read/delete calls trigger an immediate refetch in
`UnreadBadge` too) so both indicators stay in sync the moment a read action completes,
rather than relying on independent polling windows.

## root cause

`UnreadBadge` and `NotificationsPage` are two independent components that each keep
their own local unread-count state, fetched from separate API calls, with no shared
state or event connecting them. Marking a notification read updates
`NotificationsPage`'s own state correctly, but there is nothing that also tells
`UnreadBadge` to refresh — it only updates on its own 30-second poll interval, which
is unrelated to any read/delete action the user takes.

## resolution (branch `fix/unread-badge-stale-count`)

Lifted the unread count into a shared `NotificationsProvider`
(`apps/frontend/src/lib/notifications/NotificationsContext.tsx`), mirroring the
existing `AuthContext` pattern:

- The provider owns `unreadCount` and a `refresh()` function, fetches it on mount
  and polls every 30s while authenticated (same behavior `UnreadBadge` used to own
  itself), and is mounted once at the app root (`app.tsx`, inside `AuthProvider`
  since it depends on `token`).
- `UnreadBadge` is now a thin consumer (`useNotificationsContext().unreadCount`) with
  no state or polling of its own.
- `NotificationsPage` calls the shared `refresh()` (alongside its own `load()`) after
  `onMarkRead`, `onMarkAll`, and `onDelete`, so the sidebar badge updates in the same
  render pass as the page's own count — no more waiting on an unrelated 30s window.

Verified with a new regression test in `NotificationsPage.spec.tsx` that renders
`UnreadBadge` and `NotificationsPage` together under one `NotificationsProvider` and
asserts the badge disappears immediately after clicking "Mark read" — it must not
wait for a separate poll. Also updated `DashboardLayout.spec.tsx` and the existing
`NotificationsPage.spec.tsx` test to wrap with `NotificationsProvider`. Full frontend
suite (23 files / 46 tests) and `tsc` typecheck pass.
