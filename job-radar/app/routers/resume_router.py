from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas
from app.auth import get_current_user

router = APIRouter(prefix="/resumes", tags=["resumes"])


@router.post("", response_model=schemas.ResumeOut, status_code=201)
def create_resume(
    payload: schemas.ResumeCreate,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    # Only one active resume per user for simplicity — deactivate old ones.
    db.query(models.Resume).filter(models.Resume.user_id == user.id).update({"is_active": False})
    resume = models.Resume(user_id=user.id, content_text=payload.content_text, is_active=True)
    db.add(resume)
    db.commit()
    db.refresh(resume)
    return resume


@router.get("/me", response_model=schemas.ResumeOut)
def get_my_resume(db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    resume = (
        db.query(models.Resume)
        .filter(models.Resume.user_id == user.id, models.Resume.is_active == True)  # noqa: E712
        .order_by(models.Resume.created_at.desc())
        .first()
    )
    if not resume:
        raise HTTPException(status_code=404, detail="No resume on file yet")
    return resume
