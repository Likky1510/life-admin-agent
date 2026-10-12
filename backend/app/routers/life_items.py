from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.deps import get_current_user
from app.models.models import User, LifeItem, ItemType, RecurrenceType
from app.models.schemas import LifeItemCreate, LifeItemUpdate, LifeItemOut
from app.agents.reminder_agent import get_next_occurrence

router = APIRouter(prefix="/life-items", tags=["life-items"])


@router.post("", response_model=LifeItemOut, status_code=201)
def create_life_item(
    payload: LifeItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    item = LifeItem(user_id=current_user.id, **payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.get("", response_model=List[LifeItemOut])
def list_life_items(
    item_type: Optional[ItemType] = None,
    include_completed: bool = True,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(LifeItem).filter(LifeItem.user_id == current_user.id)
    if item_type:
        query = query.filter(LifeItem.item_type == item_type)
    if not include_completed:
        query = query.filter(LifeItem.is_completed == False)  # noqa: E712
    return query.order_by(LifeItem.due_date.asc()).all()


@router.get("/upcoming", response_model=List[LifeItemOut])
def upcoming_items(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Used by the Dashboard -- everything not yet completed, soonest first."""
    return (
        db.query(LifeItem)
        .filter(LifeItem.user_id == current_user.id, LifeItem.is_completed == False)  # noqa: E712
        .order_by(LifeItem.due_date.asc())
        .all()
    )


@router.patch("/{item_id}", response_model=LifeItemOut)
def update_life_item(
    item_id: str,
    payload: LifeItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    item = db.query(LifeItem).filter(LifeItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if item.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your item")

    update_data = payload.model_dump(exclude_unset=True)
    was_completed = item.is_completed
    for key, value in update_data.items():
        setattr(item, key, value)

    # If this item just got marked completed and it's recurring, spawn the
    # next occurrence automatically -- this is the actual "recurring
    # reminders" behavior, not just a label on the item.
    just_completed = update_data.get("is_completed") and not was_completed
    if just_completed:
        item.completed_at = datetime.utcnow()
        if item.recurrence != RecurrenceType.none:
            next_due = get_next_occurrence(item.due_date, item.recurrence)
            if next_due:
                db.add(LifeItem(
                    user_id=current_user.id, item_type=item.item_type,
                    title=item.title, description=item.description,
                    due_date=next_due, amount=item.amount, recurrence=item.recurrence,
                ))

    db.commit()
    db.refresh(item)
    return item


@router.delete("/{item_id}", status_code=204)
def delete_life_item(
    item_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    item = db.query(LifeItem).filter(LifeItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if item.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your item")
    db.delete(item)
    db.commit()
    return None
