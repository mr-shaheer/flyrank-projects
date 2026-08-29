from typing import Dict, Any
from uuid import uuid4

jobs: Dict[str, Dict[str, Any]] = {}


def create_job(resume_text: str) -> str:
    job_id = str(uuid4())

    jobs[job_id] = {
        "id": job_id,
        "resume_text": resume_text,
        "status": "queued",
        "result": None,
        "error": None,
        "retries": 0,
    }

    return job_id


def get_job(job_id: str):
    return jobs.get(job_id)


def update_status(job_id: str, status: str):
    if job_id in jobs:
        jobs[job_id]["status"] = status


def save_result(job_id: str, result):
    if job_id in jobs:
        jobs[job_id]["status"] = "completed"
        jobs[job_id]["result"] = result


def save_error(job_id: str, error: str):
    if job_id in jobs:
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["error"] = error


def increment_retry(job_id: str):
    if job_id in jobs:
        jobs[job_id]["retries"] += 1