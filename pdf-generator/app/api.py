"""
api.py
------
Thin HTTP layer over jobs.py.

  POST /reports/sales             -> enqueue a job, return {id, status} immediately
  GET  /reports/{id}              -> poll job status (+ download link once done)
  GET  /reports/{id}/download     -> stream the stored PDF (the artifact link)

Note how the PDF bytes only ever flow in the /download response --
everything before that is just an id/status/path being passed around.
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

from app import jobs
from app.db import init_db
from app.scheduler import start_scheduler

app = FastAPI(title="Report Pipeline")


class ReportRequest(BaseModel):
    start_date: str  # "YYYY-MM-DD"
    end_date: str


@app.on_event("startup")
def on_startup():
    # idempotent-ish: only run init_db manually via `python -m app.db` normally;
    # here we just make sure pending jobs resume and the scheduler is live.
    jobs.requeue_pending_jobs_on_startup()
    start_scheduler()


@app.post("/reports/sales")
def create_sales_report(req: ReportRequest):
    handle = jobs.enqueue_sales_report(req.start_date, req.end_date)
    return {"id": handle.id, "status": handle.status}


@app.get("/reports/{job_id}")
def get_report_status(job_id: str):
    row = jobs.get_job(job_id)
    if row is None:
        raise HTTPException(status_code=404, detail="job not found")

    result = {
        "id": row["id"],
        "status": row["status"],
        "report_type": row["report_type"],
        "created_at": row["created_at"],
        "started_at": row["started_at"],
        "finished_at": row["finished_at"],
    }
    if row["status"] == "done":
        result["download_url"] = f"/reports/{job_id}/download"
    if row["status"] == "failed":
        result["error"] = row["error"]
    return result


@app.get("/reports/{job_id}/download")
def download_report(job_id: str):
    row = jobs.get_job(job_id)
    if row is None:
        raise HTTPException(status_code=404, detail="job not found")
    if row["status"] != "done":
        raise HTTPException(status_code=409, detail=f"job is {row['status']}, not ready")
    return FileResponse(
        row["file_path"],
        media_type="application/pdf",
        filename=f"sales_report_{job_id[:8]}.pdf",
    )
