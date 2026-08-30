"""Scraping layer.

Pulls fresh remote job postings from RemoteOK's public JSON endpoint.
If the network call fails (offline dev, sandboxed CI, rate-limited, etc.)
we fall back to a small bundled sample so the rest of the pipeline
(scoring, reporting, email) always has something to work with.
"""
import datetime as dt
import logging

import requests
from sqlalchemy.orm import Session

from app.config import settings
from app import models

logger = logging.getLogger("jobradar.scraper")

_HEADERS = {"User-Agent": "JobRadar-Internship-Capstone/1.0"}

_SAMPLE_JOBS = [
    {
        "id": "sample-1",
        "position": "Backend Engineer (Python)",
        "company": "Northwind Labs",
        "location": "Remote",
        "description": "Build and maintain REST APIs in Python/FastAPI, work with Postgres, "
                        "own background jobs and integrations with third-party services.",
        "url": "https://example.com/jobs/backend-engineer-python",
        "date": dt.datetime.utcnow().isoformat(),
    },
    {
        "id": "sample-2",
        "position": "AI Engineer",
        "company": "Vector & Co",
        "location": "Remote - US",
        "description": "Design LLM-powered features, prompt engineering, RAG pipelines, "
                        "evaluation harnesses, and production monitoring for AI systems.",
        "url": "https://example.com/jobs/ai-engineer",
        "date": dt.datetime.utcnow().isoformat(),
    },
    {
        "id": "sample-3",
        "position": "Frontend Developer (React)",
        "company": "Brightloop",
        "location": "Remote - EU",
        "description": "Build React/TypeScript interfaces, collaborate with designers, "
                        "own component library and accessibility standards.",
        "url": "https://example.com/jobs/frontend-react",
        "date": dt.datetime.utcnow().isoformat(),
    },
    {
        "id": "sample-4",
        "position": "Data Engineer",
        "company": "Ledgerline",
        "location": "Remote",
        "description": "Own ETL pipelines, orchestration (Airflow), warehouse modeling in "
                        "dbt/SQL, and data quality monitoring.",
        "url": "https://example.com/jobs/data-engineer",
        "date": dt.datetime.utcnow().isoformat(),
    },
]


def _fetch_raw_jobs(limit: int) -> list[dict]:
    try:
        resp = requests.get(settings.REMOTEOK_URL, headers=_HEADERS, timeout=8)
        resp.raise_for_status()
        data = resp.json()
        # RemoteOK's first element is a legal/meta notice, not a job.
        jobs = [item for item in data if isinstance(item, dict) and item.get("id")]
        return jobs[:limit]
    except Exception as exc:  # noqa: BLE001
        logger.warning("Live scrape failed (%s); falling back to bundled sample jobs.", exc)
        return _SAMPLE_JOBS[:limit]


def scrape_and_store_jobs(db: Session, limit: int = None) -> int:
    """Fetches postings and upserts new ones into the DB. Returns count of NEW jobs added."""
    limit = limit or settings.SCRAPE_LIMIT
    raw_jobs = _fetch_raw_jobs(limit)

    new_count = 0
    for raw in raw_jobs:
        external_id = str(raw.get("id"))
        existing = db.query(models.Job).filter(models.Job.external_id == external_id).first()
        if existing:
            continue

        posted_at = None
        date_str = raw.get("date")
        if date_str:
            try:
                posted_at = dt.datetime.fromisoformat(str(date_str).replace("Z", "+00:00")).replace(tzinfo=None)
            except ValueError:
                posted_at = None

        job = models.Job(
            external_id=external_id,
            title=raw.get("position") or raw.get("title") or "Untitled role",
            company=raw.get("company"),
            location=raw.get("location") or "Remote",
            description=raw.get("description") or "",
            url=raw.get("url"),
            source="remoteok",
            posted_at=posted_at,
        )
        db.add(job)
        new_count += 1

    db.commit()
    return new_count
