from fastapi import APIRouter, Form
import smtplib
from email.message import EmailMessage
import os

router = APIRouter()

SMTP_EMAIL = os.getenv("SMTP_EMAIL")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

@router.post("/email")
def send_meeting_email(
    to_email: str = Form(...),
    subject: str = Form(...),
    duration: str = Form(...),
    availability: str = Form(...),
    description: str = Form(...)
):
    msg = EmailMessage()
    msg["From"] = SMTP_EMAIL
    msg["To"] = to_email
    msg["Subject"] = f"Meeting Request: {subject}"

    msg.set_content(
        f"""
Meeting Request

Subject: {subject}
Duration: {duration} minutes
Available Time: {availability}

Description:
{description}

— Sent via Negotiator AI
"""
    )

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(SMTP_EMAIL, SMTP_PASSWORD)
        smtp.send_message(msg)

    return {"status": "sent"}
