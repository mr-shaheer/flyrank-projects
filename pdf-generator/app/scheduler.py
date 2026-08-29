"""
scheduler.py
------------
Stretch goal: run the same job pipeline on a recurring schedule, instead
of only on demand.

Uses APScheduler's BackgroundScheduler, which runs in the same process
and simply calls jobs.enqueue_sales_report(...) on a cron-like trigger --
it does NOT generate the PDF itself. This is intentional: the scheduler's
only responsibility is "decide when," the job system's responsibility is
"do the work." Same enqueue path as the on-demand API route, so status
tracking/storage/download all work identically for scheduled reports.
"""

import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from app import jobs

_scheduler: BackgroundScheduler | None = None


def _run_daily_report():
    """Generate a report covering the last 7 days, ending yesterday."""
    end = datetime.date.today() - datetime.timedelta(days=1)
    start = end - datetime.timedelta(days=6)
    jobs.enqueue_sales_report(start.isoformat(), end.isoformat())


def start_scheduler() -> BackgroundScheduler:
    global _scheduler
    if _scheduler is not None:
        return _scheduler

    _scheduler = BackgroundScheduler()
    # Every day at 06:00 UTC, enqueue a trailing-7-day sales report.
    _scheduler.add_job(
        _run_daily_report,
        trigger=CronTrigger(hour=6, minute=0),
        id="daily_sales_report",
        replace_existing=True,
    )
    _scheduler.start()
    return _scheduler


def stop_scheduler() -> None:
    global _scheduler
    if _scheduler is not None:
        _scheduler.shutdown(wait=False)
        _scheduler = None
