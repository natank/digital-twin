## finding description

finding: job status pending forever after uploading and prosessing a file

# applicable documents

1. technical design: `docs/TECHNICAL_DESIGN.md`
2. implementation master plan: `docs/IMPLEMENTATION_MASTER_PLAN.md`
3. screenshot: `docs/production-findings/finding-2-screenshot.png`

## investigation

infinite network requests showing in network tab,

Request URL
http://localhost:8000/profiles/me/cv/jobs/759d697b-af62-4635-a928-d9d7faba4f37
Request Method
GET
Status Code
200 OK
Remote Address
127.0.0.1:8000
Referrer Policy
strict-origin-when-cross-origin

Response:
{
"status": "success",
"data": {
"id": "759d697b-af62-4635-a928-d9d7faba4f37",
"owner_id": "8996ef50-63b3-40d6-b8b5-e798c8f292f6",
"status": "pending",
"cv_file_path": "s3://digital-twin-dev/cv-uploads/8996ef50-63b3-40d6-b8b5-e798c8f292f6/d1bb78c9-e26d-4697-a110-bc145b6e6d24-Nati_Kamusher_-_Full_Stack_Dev.pdf",
"error_message": null,
"created_at": "2026-07-25T07:44:12.248332",
"updated_at": "2026-07-25T07:44:12.248332"
},
"error": null,
"meta": {
"timestamp": "2026-07-25T08:01:06.251442Z",
"request_id": null
}
}

## next tasks

find root cause and fix on a bug branch
may instrument console logs as necessary.

## root cause

Two compounding issues:

1. **No Celery worker running (immediate cause).** The API enqueues
   `tasks.process_cv` to Redis via `.delay()` (`service.py:241`), but the
   worker process that consumes the queue was not running. Verified live:
   uvicorn + Redis + Postgres up (`docker ps`), but no `celery` process.
   The documented dev workflow (`scripts/start-dev.sh`, `README.md`) told
   developers to start the API and UI but marked the worker "Optional" /
   omitted it — so jobs sat `pending` forever with nothing to process them.

2. **Frontend polled indefinitely (the defect in the screenshot).**
   `pollJob` in `CvUploadSection.tsx` polled `/cv/jobs/{id}` every 1.5s and
   only stopped on a _terminal_ status. While the job stayed `pending` it
   polled forever with no timeout — the "infinite network requests" observed.

The backend pipeline itself was correct: starting the worker immediately
drained the queued backlog and completed the exact finding job
`759d697b-af62-4635-a928-d9d7faba4f37` in ~6s.

## resolution (branch `fix/cv-job-pending-forever`)

- Frontend: `pollJob` now caps polling at ~2 minutes (`MAX_POLL_ATTEMPTS`);
  on timeout it stops and surfaces an error instead of polling forever.
  Added a regression test covering the stuck-`pending` timeout path.
- Ops: added `pnpm worker` shortcut; `start-dev.sh` and `README.md` now list
  the worker as **required** for CV processing (no longer "Optional").
