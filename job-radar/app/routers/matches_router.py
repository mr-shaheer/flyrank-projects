from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas
from app.auth import get_current_user
from app.pipeline import score_unmatched_jobs_for_user

router = APIRouter(prefix="/matches", tags=["matches"])


@router.post("/run")
def run_matching(db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    resume = (
        db.query(models.Resume)
        .filter(models.Resume.user_id == user.id, models.Resume.is_active == True)  # noqa: E712
        .order_by(models.Resume.created_at.desc())
        .first()
    )
    if not resume:
        raise HTTPException(status_code=400, detail="Upload a resume first via POST /resumes")

    created = score_unmatched_jobs_for_user(db, user, resume)
    return {"newly_scored": created}


@router.get("/me", response_model=list[schemas.MatchOut])
def list_my_matches(db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    matches = (
        db.query(models.Match)
        .filter(models.Match.user_id == user.id)
        .order_by(models.Match.score.desc())
        .all()
    )
    return matches
