"""
Notification dispatch service. Every notification is recorded in the DB
(so the web/in-app inbox always works) and additionally "sent" via the
requested channel -- email via SMTP, push via Firebase -- both of which
log to console in mock mode instead of making a real call.
"""
import logging
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.models import Notification, NotificationChannel, User

settings = get_settings()
logger = logging.getLogger("notifications")


def _send_email(to_email: str, subject: str, body: str) -> bool:
    if settings.smtp_is_mocked:
        logger.info(f"[MOCK EMAIL] To: {to_email} | Subject: {subject}\n{body}")
        return True

    import smtplib
    from email.mime.text import MIMEText

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = settings.smtp_from_email
    msg["To"] = to_email

    try:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
            server.starttls()
            server.login(settings.smtp_username, settings.smtp_password)
            server.sendmail(settings.smtp_from_email, [to_email], msg.as_string())
        return True
    except Exception as e:
        logger.error(f"SMTP error: {e}")
        return False


def _send_push(user_id: str, title: str, body: str) -> bool:
    if settings.firebase_is_mocked:
        logger.info(f"[MOCK PUSH] To user {user_id} | {title}: {body}")
        return True

    import requests
    try:
        response = requests.post(
            "https://fcm.googleapis.com/fcm/send",
            headers={"Authorization": f"key={settings.firebase_server_key}"},
            json={"to": f"/topics/user_{user_id}", "notification": {"title": title, "body": body}},
            timeout=5,
        )
        return response.status_code == 200
    except Exception as e:
        logger.error(f"Firebase push error: {e}")
        return False


def send_notification(
    db: Session, user_id: str, channel: NotificationChannel,
    title: str, message: str, life_item_id: str = None,
) -> Notification:
    """Records the notification in the DB and dispatches it via the requested channel."""
    notification = Notification(
        user_id=user_id, life_item_id=life_item_id,
        channel=channel, title=title, message=message,
    )
    db.add(notification)
    db.flush()  # get an ID without committing yet, caller controls the transaction boundary

    if channel == NotificationChannel.email:
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            _send_email(user.email, title, message)
    elif channel == NotificationChannel.push:
        _send_push(user_id, title, message)
    # channel == web: no external dispatch needed, the DB row IS the web notification

    return notification
