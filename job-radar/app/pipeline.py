from sqlalchemy.orm import Session

from app import models
from app.llm import score_resume_against_job


def score_unmatched_jobs_for_user(db: Session, user: models.User, resume: models.Resume) -> int:
    """Scores every job the user hasn't been matched against yet.

    The `matches` table doubles as our score cache: a job already scored
    for this user is never re-sent to the LLM, which keeps this idempotent
    and cheap to re-run on every scheduler tick.
    """
    already_scored_job_ids = {
        row[0] for row in db.query(models.Match.job_id).filter(models.Match.user_id == user.id).all()
    }
    unscored_jobs = db.query(models.Job).filter(~models.Job.id.in_(already_scored_job_ids)).all() \
        if already_scored_job_ids else db.query(models.Job).all()

    created = 0
    for job in unscored_jobs:
        score, reasoning = score_resume_against_job(resume.content_text, job.title, job.description)
        match = models.Match(
            user_id=user.id,
            job_id=job.id,
            resume_id=resume.id,
            score=score,
            reasoning=reasoning,
        )
        db.add(match)
        created += 1

    if created:
        db.commit()
    return created
