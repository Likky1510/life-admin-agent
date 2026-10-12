"""
Runs the Reminder Engine automatically on a schedule, same pattern used
in both prior projects.
"""
import logging
from apscheduler.schedulers.background import BackgroundScheduler

from app.db.session import SessionLocal
from app.agents.reminder_agent import check_upcoming_items

logger = logging.getLogger("scheduler")
scheduler = BackgroundScheduler()


def _scheduled_reminder_check():
    db = SessionLocal()
    try:
        upcoming = check_upcoming_items(db)
        if upcoming:
            logger.info(f"Reminder check sent {len(upcoming)} reminder(s).")
    finally:
        db.close()


def start_scheduler():
    scheduler.add_job(_scheduled_reminder_check, "interval", hours=6, id="reminder_check")
    scheduler.start()
    logger.info("Background scheduler started (reminder check every 6h)")


def stop_scheduler():
    scheduler.shutdown(wait=False)
