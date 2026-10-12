from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field

from app.models.models import ItemType, RecurrenceType, NotificationChannel, OpportunityType


# ---------- Auth ----------
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str = Field(min_length=6)
    interests: List[str] = []
    qualifications: List[str] = []
    career_goals: List[str] = []


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: str
    name: str
    email: EmailStr
    interests: List[str]
    qualifications: List[str]
    career_goals: List[str]

    class Config:
        from_attributes = True


class UserProfileUpdate(BaseModel):
    interests: Optional[List[str]] = None
    qualifications: Optional[List[str]] = None
    career_goals: Optional[List[str]] = None


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    reset_token: str
    new_password: str = Field(min_length=6)


# ---------- Life Items ----------
class LifeItemCreate(BaseModel):
    item_type: ItemType
    title: str
    description: Optional[str] = None
    due_date: datetime
    amount: Optional[float] = None
    recurrence: RecurrenceType = RecurrenceType.none


class LifeItemUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    amount: Optional[float] = None
    recurrence: Optional[RecurrenceType] = None
    is_completed: Optional[bool] = None


class LifeItemOut(BaseModel):
    id: str
    item_type: ItemType
    title: str
    description: Optional[str]
    due_date: datetime
    amount: Optional[float]
    recurrence: RecurrenceType
    is_completed: bool
    reminder_sent: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ---------- Notifications ----------
class NotificationOut(BaseModel):
    id: str
    channel: NotificationChannel
    title: str
    message: str
    is_read: bool
    sent_at: datetime

    class Config:
        from_attributes = True


# ---------- Opportunities ----------
class OpportunityOut(BaseModel):
    id: str
    opportunity_type: OpportunityType
    title: str
    organization: Optional[str]
    description: Optional[str]
    tags: List[str]
    url: Optional[str]
    deadline: Optional[datetime]
    source: Optional[str]

    class Config:
        from_attributes = True


class OpportunityMatchOut(BaseModel):
    opportunity: OpportunityOut
    relevance_score: float
    match_reason: str


# ---------- AI Assistant ----------
class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    reply: str


class ChatMessageOut(BaseModel):
    role: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True


class DailyScheduleOut(BaseModel):
    schedule: List[str]
    summary: str


# ---------- Analytics ----------
class AnalyticsSummary(BaseModel):
    upcoming_deadlines: int
    completed_tasks: int
    pending_tasks: int
    overdue_items: int
    opportunities_available: int
    completion_rate_pct: float
    productivity_tip: Optional[str] = None
