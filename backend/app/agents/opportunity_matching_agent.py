"""
Opportunity Discovery Agent (Module 4) -- matching logic.

Uses Sentence Transformers to embed the user's profile (interests +
qualifications + career goals) and each opportunity's text, then ranks
by cosine similarity. This is the same embedding-based approach used
for job matching in the Placement Optimizer project, applied here
across a broader opportunity type (jobs, scholarships, courses, etc).
"""
from typing import List, Dict

_model = None


def _get_model():
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model


def _user_profile_text(interests: List[str], qualifications: List[str], career_goals: List[str]) -> str:
    return (
        f"Interests: {', '.join(interests)}. "
        f"Qualifications: {', '.join(qualifications)}. "
        f"Career goals: {', '.join(career_goals)}."
    )


def _opportunity_text(opp: Dict) -> str:
    return f"{opp['title']}. {opp.get('description', '')} Tags: {', '.join(opp.get('tags', []))}."


def rank_opportunities(
    interests: List[str], qualifications: List[str], career_goals: List[str],
    opportunities: List[Dict],
) -> List[Dict]:
    """
    Returns opportunities annotated with relevance_score (0-100) and a
    short match_reason, sorted by relevance descending.
    """
    if not opportunities:
        return []

    # A user with a completely empty profile has nothing to match against --
    # return everything with a neutral score rather than dividing by zero
    # or producing a meaningless embedding from an empty string.
    if not (interests or qualifications or career_goals):
        return [
            {**opp, "relevance_score": 50.0, "match_reason": "Complete your profile (interests, qualifications, career goals) for personalized matching."}
            for opp in opportunities
        ]

    model = _get_model()
    profile_text = _user_profile_text(interests, qualifications, career_goals)
    opp_texts = [_opportunity_text(o) for o in opportunities]

    profile_emb = model.encode([profile_text])[0]
    opp_embs = model.encode(opp_texts)

    import numpy as np
    profile_norm = profile_emb / np.linalg.norm(profile_emb)

    user_terms = set(t.lower() for t in interests + qualifications + career_goals)

    results = []
    for opp, opp_emb in zip(opportunities, opp_embs):
        opp_norm = opp_emb / np.linalg.norm(opp_emb)
        similarity = float(np.dot(profile_norm, opp_norm))
        score = round(max(0.0, min(1.0, similarity)) * 100, 1)

        opp_tags = set(t.lower() for t in opp.get("tags", []))
        overlap = user_terms & opp_tags
        if overlap:
            reason = f"Matches your interest in {', '.join(sorted(overlap))}."
        else:
            reason = "Semantically related to your profile."

        results.append({**opp, "relevance_score": score, "match_reason": reason})

    results.sort(key=lambda r: r["relevance_score"], reverse=True)
    return results
