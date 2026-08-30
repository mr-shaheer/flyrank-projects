import logging
import smtplib
from email.message import EmailMessage

from app.config import settings

logger = logging.getLogger("jobradar.emailer")


def send_digest_email(to_email: str, pdf_path: str, matches_count: int) -> bool:
    """Sends the PDF digest by email. Returns True if actually sent.

    If SMTP isn't configured, logs and returns False instead of crashing —
    the PDF is still generated and downloadable via the API either way.
    """
    if not (settings.SMTP_HOST and settings.SMTP_USER and settings.SMTP_PASSWORD):
        logger.info(
            "SMTP not configured — skipping email send. PDF is available at %s", pdf_path
        )
        return False

    msg = EmailMessage()
    msg["Subject"] = f"JobRadar: {matches_count} new matches for you"
    msg["From"] = settings.SMTP_FROM or settings.SMTP_USER
    msg["To"] = to_email
    msg.set_content(
        f"Hi,\n\nYour latest JobRadar digest is attached ({matches_count} scored matches).\n\n— JobRadar"
    )

    with open(pdf_path, "rb") as f:
        msg.add_attachment(
            f.read(), maintype="application", subtype="pdf", filename=pdf_path.split("/")[-1]
        )

    try:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.send_message(msg)
        logger.info("Digest email sent to %s", to_email)
        return True
    except Exception as exc:  # noqa: BLE001
        logger.error("Failed to send digest email: %s", exc)
        return False
