from sqlalchemy.orm import Session

from app import models
from app.llm import score_resume_against_job
from app.retrieval import get_top_jobs   # NEW


def score_unmatched_jobs_for_user(
    db: Session,
    user: models.User,
    resume: models.Resume
) -> int:
    """Score only the most relevant jobs using semantic retrieval first."""

    already_scored_job_ids = {
        row[0]
        for row in db.query(models.Match.job_id)
        .filter(models.Match.user_id == user.id)
        .all()
    }

    if already_scored_job_ids:
        unscored_jobs = (
            db.query(models.Job)
            .filter(~models.Job.id.in_(already_scored_job_ids))
            .all()
        )
    else:
        unscored_jobs = db.query(models.Job).all()

    # Nothing new to score
    if not unscored_jobs:
        return 0

    # NEW: Keep only the top 10 semantically similar jobs
    top_jobs = get_top_jobs(
        resume_text=resume.content_text,
        jobs=unscored_jobs,
        top_k=10,
    )

    created = 0

    for job in top_jobs:
        score, reasoning = score_resume_against_job(
            resume.content_text,
            job.title,
            job.description,
        )

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