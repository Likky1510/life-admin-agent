"""
Reminder Engine (Module 3).

Deliberately rule-based: "is this due date within N hours and not yet
reminded?" is a deterministic time comparison, same pattern as the
Grievance System's escalation agent and the Placement Optimizer's
deadline agent. Recurrence handling (creating the next occurrence after
completion) is also pure date arithmetic.
"""
import logging
import calendar
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.models.models import LifeItem, RecurrenceType, NotificationChannel
from app.agents.notification_service import send_notification

logger = logging.getLogger("agents.reminder")

REMINDER_WINDOW_HOURS = 48


def check_upcoming_items(db: Session) -> list:
    """
    Finds life items due within the reminder window that haven't been
    reminded yet, sends notifications across web/email/push, marks them
    reminded, and returns the list of items that triggered a reminder.
    """
    now = datetime.utcnow()
    window_end = now + timedelta(hours=REMINDER_WINDOW_HOURS)

    upcoming = (
        db.query(LifeItem)
        .filter(LifeItem.due_date >= now)
        .filter(LifeItem.due_date <= window_end)
        .filter(LifeItem.reminder_sent == False)  # noqa: E712
        .filter(LifeItem.is_completed == False)  # noqa: E712
        .all()
    )

    for item in upcoming:
        title = f"Upcoming {item.item_type.value}: {item.title}"
        message = _build_reminder_message(item)

        for channel in [NotificationChannel.web, NotificationChannel.email]:
            send_notification(db, user_id=item.user_id, life_item_id=item.id,
                               channel=channel, title=title, message=message)

        item.reminder_sent = True
        logger.info(f"Reminder sent for {item.item_type.value} '{item.title}' due {item.due_date}")

    db.commit()
    return upcoming


def _build_reminder_message(item: LifeItem) -> str:
    time_left = item.due_date - datetime.utcnow()
    hours_left = max(0, int(time_left.total_seconds() // 3600))

    if item.item_type.value == "bill" and item.amount:
        return f"Your bill '{item.title}' of {item.amount} is due in {hours_left} hours."
    return f"'{item.title}' is due in {hours_left} hours."


def _add_months(dt: datetime, months: int) -> datetime:
    """Pure-stdlib month addition (avoids needing python-dateutil as a dependency)."""
    month = dt.month - 1 + months
    year = dt.year + month // 12
    month = month % 12 + 1
    day = min(dt.day, calendar.monthrange(year, month)[1])
    return dt.replace(year=year, month=month, day=day)


def get_next_occurrence(due_date: datetime, recurrence: RecurrenceType):
    """Used when a recurring item is marked complete, to schedule the next one."""
    if recurrence == RecurrenceType.daily:
        return due_date + timedelta(days=1)
    if recurrence == RecurrenceType.weekly:
        return due_date + timedelta(weeks=1)
    if recurrence == RecurrenceType.monthly:
        return _add_months(due_date, 1)
    if recurrence == RecurrenceType.yearly:
        return _add_months(due_date, 12)
    return None  # RecurrenceType.none -- no next occurrence
