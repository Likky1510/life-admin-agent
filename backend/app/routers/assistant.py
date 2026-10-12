from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.deps import get_current_user
from app.models.models import User, ChatMessage, LifeItem
from app.models.schemas import ChatRequest, ChatResponse, ChatMessageOut, DailyScheduleOut
from app.agents.assistant_agent import chat_with_assistant, suggest_daily_schedule

router = APIRouter(prefix="/assistant", tags=["assistant"])

HISTORY_LIMIT = 10  # how many past messages to feed back in as context


@router.post("/chat", response_model=ChatResponse)
def chat(
    payload: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    past_messages = (
        db.query(ChatMessage)
        .filter(ChatMessage.user_id == current_user.id)
        .order_by(ChatMessage.created_at.desc())
        .limit(HISTORY_LIMIT)
        .all()
    )
    conversation_history = [
        {"role": m.role, "content": m.content} for m in reversed(past_messages)
    ]

    life_items = (
        db.query(LifeItem)
        .filter(LifeItem.user_id == current_user.id, LifeItem.is_completed == False)  # noqa: E712
        .order_by(LifeItem.due_date.asc())
        .limit(10)
        .all()
    )

    reply = chat_with_assistant(
        user_message=payload.message, user_id=current_user.id,
        life_items=life_items, conversation_history=conversation_history,
    )

    db.add(ChatMessage(user_id=current_user.id, role="user", content=payload.message))
    db.add(ChatMessage(user_id=current_user.id, role="assistant", content=reply))
    db.commit()

    return ChatResponse(reply=reply)


@router.get("/chat/history", response_model=List[ChatMessageOut])
def chat_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return (
        db.query(ChatMessage)
        .filter(ChatMessage.user_id == current_user.id)
        .order_by(ChatMessage.created_at.asc())
        .all()
    )


@router.get("/daily-schedule", response_model=DailyScheduleOut)
def daily_schedule(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    life_items = (
        db.query(LifeItem)
        .filter(LifeItem.user_id == current_user.id, LifeItem.is_completed == False)  # noqa: E712
        .order_by(LifeItem.due_date.asc())
        .limit(15)
        .all()
    )
    result = suggest_daily_schedule(life_items)
    return DailyScheduleOut(**result)
