import logging

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from app.config import settings
from app.database import SessionLocal
from app import models
from app.scraper import scrape_and_store_jobs
from app.pipeline import score_unmatched_jobs_for_user
from app.reports import generate_matches_pdf
from app.emailer import send_digest_email
from app.cache import cache

logger = logging.getLogger("jobradar.scheduler")

_scheduler: BackgroundScheduler | None = None


def run_daily_cycle():
    """The single job the cron scheduler triggers: scrape -> score -> report -> email.

    Runs for every user in the system who has an active resume.
    """
    db = SessionLocal()
    try:
        new_jobs = scrape_and_store_jobs(db)
        cache.invalidate("job_list")
        logger.info("Scraped %d new job(s).", new_jobs)

        users = db.query(models.User).all()
        for user in users:
            resume = (
                db.query(models.Resume)
                .filter(models.Resume.user_id == user.id, models.Resume.is_active == True)  # noqa: E712
                .order_by(models.Resume.created_at.desc())
                .first()
            )
            if not resume:
                continue

            score_unmatched_jobs_for_user(db, user, resume)

            matches = db.query(models.Match).filter(models.Match.user_id == user.id).all()
            if not matches:
                continue

            pdf_path = generate_matches_pdf(user, matches)
            send_digest_email(user.email, pdf_path, len(matches))
    finally:
        db.close()


def start_scheduler():
    global _scheduler
    if _scheduler is not None:
        return _scheduler

    _scheduler = BackgroundScheduler()
    _scheduler.add_job(
        run_daily_cycle,
        trigger=CronTrigger(hour=settings.DAILY_RUN_HOUR, minute=0),
        id="daily_jobradar_cycle",
        replace_existing=True,
    )
    _scheduler.start()
    logger.info("Scheduler started: daily cycle runs at %02d:00.", settings.DAILY_RUN_HOUR)
    return _scheduler


def stop_scheduler():
    global _scheduler
    if _scheduler is not None:
        _scheduler.shutdown(wait=False)
        _scheduler = None
