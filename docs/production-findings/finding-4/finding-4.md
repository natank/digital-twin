## finding description

the tween answers doesn't match the resume apploaded

## applicable documents

1. technical design: `docs/TECHNICAL_DESIGN.md`
2. implementation master plan: `docs/IMPLEMENTATION_MASTER_PLAN.md`
3. screen capture: `docs/production-findings/finding-4/Screenshot 2026-07-25 at 12.23.24.png`
4. resume: `docs/production-findings/finding-4/Nati Kamusher - Full Stack Dev.pdf`

## next tasks

see screen capture (ref 3) with sample answer not matching the resume uploaded, (ref 4)
find root cause and fix on a bug branch

## root cause

The dashboard's "Public chat" link (`apps/frontend/src/pages/DashboardPage.tsx`) points to the
bare `/chat` route with no `?owner=` query param. `ChatWidget` (`apps/frontend/src/components/chat/ChatWidget.tsx:24`)
falls back to `getDemoOwnerId()` (i.e. `VITE_DEMO_OWNER_ID`) whenever no owner id is supplied, which
resolves to the seeded "Sample Owner" demo account (`apps/backend/scripts/seed_data.py`) —
hardcoded `skills=["Python", "TypeScript", "FastAPI"]`, headline "Software Engineer".

The screenshot's chat header reads "Sample · Software Engineer", confirming the widget was chatting
with the seeded demo profile, not the profile generated from the uploaded resume. This is why the
AI's answer ("React isn't listed among my core technical skills...") doesn't match the uploaded
résumé — it was never talking about that résumé's owner at all.

Verified independently: PDF text extraction (`apps/backend/src/profiles/extraction.py`) correctly
pulls "React" out of the uploaded résumé (confirmed by running the extractor directly against the
PDF), and no code path between extraction → LLM summary → chat system prompt filters or truncates
skills in a way that would drop "React". The bug is purely a missing `owner` id on the dashboard's
chat-preview link, not a parsing/prompt bug.

### Fix

Pass the logged-in owner's id to the chat preview link from the dashboard so "Public chat" actually
previews the current owner's own twin instead of the seeded demo profile.
