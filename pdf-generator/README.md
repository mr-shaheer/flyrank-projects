# Report Pipeline

A small end-to-end pipeline: query data with SQL → render a PDF report →
generate it as a background job, on demand now and on a schedule for the
stretch goal.

## Architecture

```
Client (API / CLI)
      │
      │ POST /reports/sales {start_date, end_date}
      ▼
jobs.enqueue_sales_report()          <- writes `pending` row, returns immediately
      │  (job id put on an in-process queue.Queue)
      ▼
worker thread(s)                     <- picks up job id, marks `running`
      │
      ▼
queries.py  (SQL aggregation) ──► report.py (reportlab PDF) ──► storage/<job_id>.pdf
      │
      ▼
report_jobs row updated: status=`done`, file_path=storage/<job_id>.pdf
      │
      ▼
Client polls GET /reports/{id} → sees `download_url`
Client GET /reports/{id}/download → PDF bytes streamed (only here!)
```

### Why it's built this way

- **SQL does the aggregation** (`queries.py`). Grouping/summing happens in
  the database, not by looping over rows in Python.
- **Rendering is separate from job orchestration** (`report.py` doesn't
  know it's running in a background job — it's just a pure function of
  `(start_date, end_date, output_path) -> Path`). That makes it directly
  unit-testable without touching the queue/worker machinery at all.
- **Store and link, don't pass bytes around.** The worker writes the PDF
  to `storage/` and the job row only ever holds a *path*. The job queue,
  the DB, and every API response except the final `/download` call carry
  only an id/status/path — never the actual PDF payload. This avoids
  bloating queue messages/DB rows and keeps job status checks cheap.
- **Job pattern is swappable.** `jobs.py` uses stdlib `queue.Queue` +
  daemon worker threads so the whole thing runs with zero extra infra.
  Swapping in Celery/RQ/SQS later only touches `jobs.py` — `report.py`
  and `queries.py` don't change.
- **Scheduling is a thin wrapper around the same enqueue path**
  (`scheduler.py`). APScheduler's only job is deciding *when*; it calls
  the exact same `enqueue_sales_report()` the API uses, so scheduled and
  on-demand reports get identical status tracking, storage, and download
  behavior for free.

## Project layout

```
app/
  db.py         SQLite schema + seed data
  queries.py    SQL aggregation queries
  report.py     Query results -> PDF (reportlab)
  jobs.py       Background job queue/worker + status tracking
  scheduler.py  Recurring job trigger (stretch goal)
  api.py        FastAPI endpoints (on-demand trigger, status, download)
demo.py         Runs the whole pipeline with no server needed
storage/        Generated PDFs live here (gitignored, created at runtime)
data/           SQLite DB file lives here (gitignored, created at runtime)
.gitignore      Excludes venvs, generated DB/PDF files, caches, env files
```

## Running it

```bash
pip install -r requirements.txt

# Option A: no server, just run the pipeline end to end
python demo.py

# Option B: run as an API
uvicorn app.api:app --reload
# then:
curl -X POST localhost:8000/reports/sales \
  -H "Content-Type: application/json" \
  -d '{"start_date": "2026-01-01", "end_date": "2026-03-31"}'
# -> {"id": "...", "status": "pending"}

curl localhost:8000/reports/<id>
# -> {"status": "done", "download_url": "/reports/<id>/download", ...}

curl -OJ localhost:8000/reports/<id>/download
```

The scheduler starts automatically with the API (`app/api.py`'s startup
hook) and enqueues a trailing-7-day sales report every day at 06:00 UTC —
using the exact same `enqueue_sales_report()` path as the on-demand route.

## Notes / what a production version would add

- Swap SQLite → Postgres and `queue.Queue` → Celery/RQ with a real broker
  (Redis/SQS) for multi-process/multi-machine workers.
- Swap local `storage/` → S3/GCS, and `file_path` → object key + presigned
  URL, so `/download` redirects instead of streaming from local disk.
- Requeue jobs that were `running` at crash time (currently only
  `pending` jobs are recovered on startup — see the docstring in
  `jobs.requeue_pending_jobs_on_startup`).
- Auth on the API routes, and per-user scoping of jobs/reports.
- Input validation on `start_date`/`end_date` (format + `start <= end`).
- Automated tests (e.g. `tests/test_report.py` exercising `report.py`
  directly, and `tests/test_jobs.py` exercising the queue/worker with a
  temp DB and temp storage dir).
