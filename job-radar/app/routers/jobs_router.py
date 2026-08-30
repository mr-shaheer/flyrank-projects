from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas
from app.auth import get_current_user
from app.cache import cache
from app.config import settings
from app.scraper import scrape_and_store_jobs

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("", response_model=list[schemas.JobOut])
def list_jobs(
    limit: int = 50,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    cache_key = f"job_list:{limit}"
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    jobs = db.query(models.Job).order_by(models.Job.scraped_at.desc()).limit(limit).all()
    result = [schemas.JobOut.model_validate(j) for j in jobs]
    cache.set(cache_key, result, settings.JOB_LIST_CACHE_TTL_SECONDS)
    return result


@router.post("/scrape")
def trigger_scrape(db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    """Manually triggers a scrape — same routine the daily cron job calls."""
    new_count = scrape_and_store_jobs(db)
    cache.invalidate()  # job list changed, drop cached pages
    return {"new_jobs_added": new_count}
