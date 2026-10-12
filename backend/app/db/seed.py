"""
Seeds the database with a demo user, sample tasks/bills/appointments,
and opportunities pulled through the (mocked) opportunity source
adapters. Run with: python -m app.db.seed
"""
from datetime import datetime, timedelta

from app.db.session import SessionLocal, Base, engine
from app.models.models import User, LifeItem, ItemType, RecurrenceType, Opportunity
from app.core.security import hash_password
from app.agents.opportunity_sources import (
    fetch_jobs_and_internships, fetch_scholarships, fetch_government_schemes,
    fetch_courses, fetch_hackathons,
)

SAMPLE_LIFE_ITEMS = [
    {"item_type": ItemType.bill, "title": "Electricity Bill", "amount": 1450.0,
     "due_date_offset_hours": 20, "recurrence": RecurrenceType.monthly},
    {"item_type": ItemType.subscription, "title": "Netflix Subscription", "amount": 499.0,
     "due_date_offset_hours": 36, "recurrence": RecurrenceType.monthly},
    {"item_type": ItemType.appointment, "title": "Dentist Appointment",
     "due_date_offset_hours": 30, "recurrence": RecurrenceType.none},
    {"item_type": ItemType.task, "title": "Submit scholarship application",
     "due_date_offset_hours": 12, "recurrence": RecurrenceType.none},
    {"item_type": ItemType.document, "title": "Passport Renewal Deadline",
     "due_date_offset_hours": 24 * 10, "recurrence": RecurrenceType.none},
    {"item_type": ItemType.task, "title": "Finish ML course module 3",
     "due_date_offset_hours": 24 * 3, "recurrence": RecurrenceType.none},
]


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        # ---- Demo user ----
        demo_email = "user@example.com"
        existing = db.query(User).filter(User.email == demo_email).first()
        if not existing:
            user = User(
                name="Demo User", email=demo_email,
                hashed_password=hash_password("user1234"),
                interests=["machine learning", "web development"],
                qualifications=["B.Tech Computer Science"],
                career_goals=["data scientist", "software engineer"],
            )
            db.add(user)
            db.commit()
            print(f"Seeded demo user: {demo_email} / user1234")
        else:
            user = existing
            print("Demo user already exists.")

        # ---- Sample life items ----
        if db.query(LifeItem).filter(LifeItem.user_id == user.id).count() == 0:
            for spec in SAMPLE_LIFE_ITEMS:
                due_date = datetime.utcnow() + timedelta(hours=spec["due_date_offset_hours"])
                db.add(LifeItem(
                    user_id=user.id, item_type=spec["item_type"], title=spec["title"],
                    due_date=due_date, amount=spec.get("amount"), recurrence=spec["recurrence"],
                ))
            db.commit()
            print(f"Seeded {len(SAMPLE_LIFE_ITEMS)} life items.")
        else:
            print("Life items already exist, skipping.")

        # ---- Opportunities (via mocked source adapters) ----
        if db.query(Opportunity).count() == 0:
            fetched = []
            for opp in fetch_jobs_and_internships():
                fetched.append({**opp, "opportunity_type": "job", "source": "LinkedIn Jobs (mock)"})
            for opp in fetch_scholarships():
                fetched.append({**opp, "opportunity_type": "scholarship", "source": "Scholarship Portal (mock)"})
            for opp in fetch_government_schemes():
                fetched.append({**opp, "opportunity_type": "government_scheme", "source": "Gov Open Data (mock)"})
            for opp in fetch_courses():
                fetched.append({**opp, "opportunity_type": "course", "source": "Coursera (mock)"})
            for opp in fetch_hackathons():
                fetched.append({**opp, "opportunity_type": "hackathon", "source": "DevCommunity (mock)"})

            for opp in fetched:
                db.add(Opportunity(
                    opportunity_type=opp["opportunity_type"], title=opp["title"],
                    organization=opp.get("organization"), description=opp.get("description"),
                    tags=opp.get("tags", []), url=opp.get("url"), deadline=opp.get("deadline"),
                    source=opp.get("source"),
                ))
            db.commit()
            print(f"Seeded {len(fetched)} opportunities via mock source adapters.")
        else:
            print("Opportunities already exist, skipping.")

    finally:
        db.close()


if __name__ == "__main__":
    seed()
