"""
ORM models for the Autonomous Life Admin & Opportunity Discovery Agent.

Covers: Users, Tasks, Bills, Subscriptions, Appointments, Documents,
Notifications, Opportunities, ChatMessages.
"""
import enum
import uuid
from datetime import datetime

from sqlalchemy import (
    Column, String, Text, DateTime, ForeignKey, Enum, Integer, Float, Boolean, JSON
)
from sqlalchemy.orm import relationship

from app.db.session import Base


def gen_uuid():
    return str(uuid.uuid4())


class ItemType(str, enum.Enum):
    task = "task"
    bill = "bill"
    subscription = "subscription"
    appointment = "appointment"
    document = "document"


class RecurrenceType(str, enum.Enum):
    none = "none"
    daily = "daily"
    weekly = "weekly"
    monthly = "monthly"
    yearly = "yearly"


class NotificationChannel(str, enum.Enum):
    web = "web"
    email = "email"
    push = "push"


class OpportunityType(str, enum.Enum):
    job = "job"
    internship = "internship"
    scholarship = "scholarship"
    government_scheme = "government_scheme"
    course = "course"
    hackathon = "hackathon"


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=gen_uuid)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    phone = Column(String, nullable=True)

    # Profile signals used by the Opportunity Discovery Module
    interests = Column(JSON, default=list)        # e.g. ["machine learning", "web development"]
    qualifications = Column(JSON, default=list)   # e.g. ["B.Tech CSE"]
    career_goals = Column(JSON, default=list)      # e.g. ["data scientist", "ML engineer"]

    created_at = Column(DateTime, default=datetime.utcnow)

    life_items = relationship("LifeItem", back_populates="user")
    notifications = relationship("Notification", back_populates="user")
    chat_messages = relationship("ChatMessage", back_populates="user")


class LifeItem(Base):
    """
    Unified table for tasks, bills, subscriptions, appointments, and
    document-expiry tracking. A single table with an item_type discriminator
    avoids 5 nearly-identical tables and makes the Reminder Engine and
    Analytics Dashboard simpler -- both just query LifeItem regardless of
    which module created the row.
    """
    __tablename__ = "life_items"

    id = Column(String, primary_key=True, default=gen_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)

    item_type = Column(Enum(ItemType), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)

    due_date = Column(DateTime, nullable=False)
    amount = Column(Float, nullable=True)  # for bills/subscriptions
    recurrence = Column(Enum(RecurrenceType), default=RecurrenceType.none)

    is_completed = Column(Boolean, default=False)
    completed_at = Column(DateTime, nullable=True)

    reminder_sent = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="life_items")


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(String, primary_key=True, default=gen_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    life_item_id = Column(String, ForeignKey("life_items.id"), nullable=True)

    channel = Column(Enum(NotificationChannel), nullable=False)
    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    sent_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="notifications")


class Opportunity(Base):
    """
    Opportunities fetched from external sources (mocked by default --
    see app/agents/opportunity_sources.py). Shared across all users;
    per-user relevance is computed at query time, not stored per-user,
    since the same job posting is relevant to many users.
    """
    __tablename__ = "opportunities"

    id = Column(String, primary_key=True, default=gen_uuid)
    opportunity_type = Column(Enum(OpportunityType), nullable=False)
    title = Column(String, nullable=False)
    organization = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    tags = Column(JSON, default=list)  # e.g. ["python", "remote", "entry-level"]
    url = Column(String, nullable=True)
    deadline = Column(DateTime, nullable=True)
    source = Column(String, nullable=True)  # e.g. "LinkedIn Jobs", "Coursera"
    fetched_at = Column(DateTime, default=datetime.utcnow)


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(String, primary_key=True, default=gen_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    role = Column(String, nullable=False)  # "user" | "assistant"
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="chat_messages")
