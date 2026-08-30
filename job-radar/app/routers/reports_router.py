from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app import models
from app.auth import get_current_user
from app.reports import generate_matches_pdf
from app.emailer import send_digest_email

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/me")
def download_my_report(db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    matches = db.query(models.Match).filter(models.Match.user_id == user.id).all()
    pdf_path = generate_matches_pdf(user, matches)
    return FileResponse(pdf_path, media_type="application/pdf", filename=pdf_path.split("/")[-1])


@router.post("/email-me")
def email_my_report(db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    matches = db.query(models.Match).filter(models.Match.user_id == user.id).all()
    pdf_path = generate_matches_pdf(user, matches)
    sent = send_digest_email(user.email, pdf_path, len(matches))
    return {"emailed": sent, "pdf_path": pdf_path}
