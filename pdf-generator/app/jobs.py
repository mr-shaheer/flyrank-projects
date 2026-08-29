"""
jobs.py
-------
Background job pattern:

  enqueue()  -> writes a `pending` row to report_jobs, puts job id on a queue,
                returns immediately (caller never blocks on PDF generation)
  worker()   -> pulls job ids off the queue, marks `running`, does the work,
                marks `done`/`failed`

Key design choice ("store and link, don't pass 20MB around"):
  The worker writes the PDF to disk under storage/ and stores only the
  *file path* in report_jobs.file_path. Nothing about the job queue, the
  DB row, or any API response ever carries raw PDF bytes -- callers fetch
  the artifact separately via that stored link (see api.py's /download
  route).

This uses Python's stdlib queue + a daemon thread pool so the whole
project runs with zero extra infrastructure (no Redis/Celery needed to
demo the pattern). Swapping in Celery/RQ later means replacing this file
only -- report.py and queries.py don't change.
"""

import json
import queue
import threading
import traceback
import uuid
import datetime
from pathlib import Path
from dataclasses import dataclass

from app.db import get_connection
from app.report import build_sales_report

STORAGE_DIR = Path(__file__).resolve().parent.parent / "storage"

_job_queue: "queue.Queue[str]" = queue.Queue()
_workers_started = False
_lock = threading.Lock()


@dataclass
class JobHandle:
    id: str
    status: str


def _now() -> str:
    return datetime.datetime.utcnow().isoformat()


def enqueue_sales_report(start_date: str, end_date: str) -> JobHandle:
    """Create a job row (status=pending) and hand it to the queue. Non-blocking."""
    job_id = str(uuid.uuid4())
    params = json.dumps({"start_date": start_date, "end_date": end_date})

    conn = get_connection()
    conn.execute(
        """INSERT INTO report_jobs (id, status, report_type, params, created_at)
           VALUES (?, 'pending', 'sales_summary', ?, ?)""",
        (job_id, params, _now()),
    )
    conn.commit()
    conn.close()

    _ensure_workers_started()
    _job_queue.put(job_id)
    return JobHandle(id=job_id, status="pending")


def get_job(job_id: str):
    conn = get_connection()
    row = conn.execute("SELECT * FROM report_jobs WHERE id = ?", (job_id,)).fetchone()
    conn.close()
    return row


def _process_job(job_id: str) -> None:
    conn = get_connection()
    row = conn.execute("SELECT * FROM report_jobs WHERE id = ?", (job_id,)).fetchone()
    if row is None:
        conn.close()
        return

    conn.execute(
        "UPDATE report_jobs SET status='running', started_at=? WHERE id=?",
        (_now(), job_id),
    )
    conn.commit()

    try:
        params = json.loads(row["params"])
        output_path = STORAGE_DIR / f"{job_id}.pdf"
        build_sales_report(params["start_date"], params["end_date"], output_path)

        conn.execute(
            """UPDATE report_jobs
               SET status='done', file_path=?, finished_at=?
               WHERE id=?""",
            (str(output_path), _now(), job_id),
        )
    except Exception:
        err = traceback.format_exc()
        conn.execute(
            "UPDATE report_jobs SET status='failed', error=?, finished_at=? WHERE id=?",
            (err, _now(), job_id),
        )
    finally:
        conn.commit()
        conn.close()


def _worker_loop() -> None:
    while True:
        job_id = _job_queue.get()
        try:
            _process_job(job_id)
        finally:
            _job_queue.task_done()


def _ensure_workers_started(num_workers: int = 2) -> None:
    global _workers_started
    with _lock:
        if _workers_started:
            return
        for _ in range(num_workers):
            t = threading.Thread(target=_worker_loop, daemon=True)
            t.start()
        _workers_started = True


def requeue_pending_jobs_on_startup() -> None:
    """
    Recovery: if the process restarted while jobs were pending/running,
    put pending ones back on the queue so they still get picked up.
    (Jobs that were 'running' at crash time are left as-is here for
    simplicity -- a production version would also requeue those after
    checking a heartbeat/lease.)
    """
    conn = get_connection()
    rows = conn.execute("SELECT id FROM report_jobs WHERE status='pending'").fetchall()
    conn.close()
    _ensure_workers_started()
    for row in rows:
        _job_queue.put(row["id"])
