"""
Analytics Dashboard (Module 6).

All the actual counting is deterministic aggregation -- same pattern
used successfully in both prior projects (Grievance System, Placement
Optimizer): SQL/Python does the arithmetic, Claude (optional) only
turns it into a short human-readable tip.
"""
from datetime import datetime
from sqlalchemy.orm import Session

from app.models.models import LifeItem, Opportunity
from app.agents.claude_client import call_claude_text


def get_analytics_summary(db: Session, user_id: str) -> dict:
    now = datetime.utcnow()

    items = db.query(LifeItem).filter(LifeItem.user_id == user_id).all()

    completed = [i for i in items if i.is_completed]
    pending = [i for i in items if not i.is_completed]
    overdue = [i for i in pending if i.due_date < now]
    upcoming = [i for i in pending if i.due_date >= now]

    total = len(items)
    completion_rate = round((len(completed) / total) * 100, 1) if total > 0 else 0.0

    opportunities_count = db.query(Opportunity).count()

    mock_tip = (
        "You're overdue on some items -- tackling the oldest one first usually clears the most mental load."
        if overdue else
        "You're on top of your deadlines -- consider checking the Opportunity Discovery module for something new."
    )
    tip = call_claude_text(
        system_prompt="You are a productivity coach. Give one short, specific, encouraging tip in a single sentence.",
        user_prompt=f"User has {len(upcoming)} upcoming items, {len(overdue)} overdue items, "
                    f"{len(completed)} completed items, completion rate {completion_rate}%.",
        mock_response=mock_tip,
        max_tokens=100,
    )

    return {
        "upcoming_deadlines": len(upcoming),
        "completed_tasks": len(completed),
        "pending_tasks": len(pending),
        "overdue_items": len(overdue),
        "opportunities_available": opportunities_count,
        "completion_rate_pct": completion_rate,
        "productivity_tip": tip,
    }
