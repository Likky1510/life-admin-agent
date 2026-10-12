from typing import List, Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.deps import get_current_user
from app.models.models import User, Opportunity, OpportunityType
from app.models.schemas import OpportunityMatchOut, OpportunityOut
from app.agents.opportunity_matching_agent import rank_opportunities
from app.agents.assistant_agent import summarize_opportunities

router = APIRouter(prefix="/opportunities", tags=["opportunities"])


@router.get("/matches", response_model=List[OpportunityMatchOut])
def get_matched_opportunities(
    opportunity_type: Optional[OpportunityType] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Opportunity)
    if opportunity_type:
        query = query.filter(Opportunity.opportunity_type == opportunity_type)
    opportunities = query.all()

    opp_dicts = [
        {
            "id": o.id, "opportunity_type": o.opportunity_type, "title": o.title,
            "organization": o.organization, "description": o.description,
            "tags": o.tags or [], "url": o.url, "deadline": o.deadline, "source": o.source,
        }
        for o in opportunities
    ]

    ranked = rank_opportunities(
        interests=current_user.interests or [],
        qualifications=current_user.qualifications or [],
        career_goals=current_user.career_goals or [],
        opportunities=opp_dicts,
    )

    return [
        OpportunityMatchOut(
            opportunity=OpportunityOut(**{k: v for k, v in r.items() if k not in ("relevance_score", "match_reason")}),
            relevance_score=r["relevance_score"],
            match_reason=r["match_reason"],
        )
        for r in ranked
    ]


@router.get("/summary")
def get_opportunities_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """AI-generated plain-English summary of the user's top matches."""
    opportunities = db.query(Opportunity).all()
    opp_dicts = [
        {"id": o.id, "title": o.title, "organization": o.organization,
         "description": o.description, "tags": o.tags or []}
        for o in opportunities
    ]
    ranked = rank_opportunities(
        interests=current_user.interests or [],
        qualifications=current_user.qualifications or [],
        career_goals=current_user.career_goals or [],
        opportunities=opp_dicts,
    )
    top_matches = ranked[:5]
    summary = summarize_opportunities(top_matches)
    return {"summary": summary}
