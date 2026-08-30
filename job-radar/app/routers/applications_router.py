from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas
from app.auth import get_current_user

router = APIRouter(prefix="/applications", tags=["applications"])


@router.post("", response_model=schemas.ApplicationOut, status_code=201)
def create_application(
    payload: schemas.ApplicationCreate,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    job = db.query(models.Job).filter(models.Job.id == payload.job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    existing = (
        db.query(models.Application)
        .filter(models.Application.user_id == user.id, models.Application.job_id == payload.job_id)
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="Application already tracked for this job")

    app_row = models.Application(
        user_id=user.id, job_id=payload.job_id, status=payload.status, notes=payload.notes
    )
    db.add(app_row)
    db.commit()
    db.refresh(app_row)
    return app_row


@router.get("/me", response_model=list[schemas.ApplicationOut])
def list_my_applications(db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    return db.query(models.Application).filter(models.Application.user_id == user.id).all()


@router.patch("/{application_id}", response_model=schemas.ApplicationOut)
def update_application(
    application_id: int,
    payload: schemas.ApplicationUpdate,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    app_row = (
        db.query(models.Application)
        .filter(models.Application.id == application_id, models.Application.user_id == user.id)
        .first()
    )
    if not app_row:
        raise HTTPException(status_code=404, detail="Application not found")

    if payload.status is not None:
        app_row.status = payload.status
    if payload.notes is not None:
        app_row.notes = payload.notes

    db.commit()
    db.refresh(app_row)
    return app_row
