"""
Opportunity source adapters (Module 4).

Each function represents one external source the approach doc names
(LinkedIn Jobs, Google Jobs, Coursera, government open data, hackathon
sites). In mock mode, each returns realistic sample listings through
the exact same return shape a real API call would -- so wiring in a
real API later means replacing the function body, not the call sites
or the data model.
"""
from datetime import datetime, timedelta
from app.core.config import get_settings

settings = get_settings()

MOCK_JOBS = [
    {"title": "Junior Python Developer", "organization": "TechNova Solutions",
     "description": "Entry-level role building backend services in Python and FastAPI.",
     "tags": ["python", "fastapi", "sql", "entry-level"], "url": "https://example.com/jobs/1"},
    {"title": "Data Analyst", "organization": "Insight Analytics",
     "description": "Analyze business data and build dashboards using SQL and Tableau.",
     "tags": ["sql", "tableau", "data analysis"], "url": "https://example.com/jobs/2"},
    {"title": "Machine Learning Intern", "organization": "DeepLogic AI",
     "description": "Support the ML team building and evaluating models.",
     "tags": ["python", "machine learning", "internship"], "url": "https://example.com/jobs/3"},
]

MOCK_SCHOLARSHIPS = [
    {"title": "National Merit Scholarship for STEM Students", "organization": "Ministry of Education",
     "description": "Need-based scholarship for undergraduate STEM students.",
     "tags": ["scholarship", "stem", "undergraduate"], "url": "https://example.com/scholarships/1"},
    {"title": "Women in Tech Scholarship", "organization": "TechForward Foundation",
     "description": "Supports women pursuing degrees in computer science and engineering.",
     "tags": ["scholarship", "women in tech", "computer science"], "url": "https://example.com/scholarships/2"},
]

MOCK_GOV_SCHEMES = [
    {"title": "Skill India Digital Upskilling Program", "organization": "Government Skill Development Portal",
     "description": "Free certification courses in digital skills for students and job seekers.",
     "tags": ["government scheme", "upskilling", "free certification"], "url": "https://example.com/schemes/1"},
]

MOCK_COURSES = [
    {"title": "Machine Learning Specialization", "organization": "Coursera",
     "description": "Foundational ML course covering supervised and unsupervised learning.",
     "tags": ["machine learning", "python", "course"], "url": "https://example.com/courses/1"},
    {"title": "Full-Stack Web Development", "organization": "Coursera",
     "description": "Covers React, Node.js, and REST API design.",
     "tags": ["javascript", "react", "node", "course"], "url": "https://example.com/courses/2"},
]

MOCK_HACKATHONS = [
    {"title": "AI for Good Hackathon", "organization": "DevCommunity",
     "description": "48-hour hackathon building AI solutions for social impact.",
     "tags": ["hackathon", "machine learning", "social impact"], "url": "https://example.com/hackathons/1"},
]


def _attach_deadlines(items: list, days_from_now: int = 21) -> list:
    return [{**item, "deadline": datetime.utcnow() + timedelta(days=days_from_now)} for item in items]


def fetch_jobs_and_internships() -> list:
    if settings.opportunities_are_mocked:
        return _attach_deadlines(MOCK_JOBS, 30)
    # Real implementation would call LinkedIn Jobs API / Google Jobs API here,
    # using settings for API keys, and return the same shape as MOCK_JOBS.
    raise NotImplementedError("Real job API integration not configured.")


def fetch_scholarships() -> list:
    if settings.opportunities_are_mocked:
        return _attach_deadlines(MOCK_SCHOLARSHIPS, 45)
    raise NotImplementedError("Real scholarship API integration not configured.")


def fetch_government_schemes() -> list:
    if settings.opportunities_are_mocked:
        return _attach_deadlines(MOCK_GOV_SCHEMES, 60)
    raise NotImplementedError("Real government open data API integration not configured.")


def fetch_courses() -> list:
    if settings.opportunities_are_mocked:
        return _attach_deadlines(MOCK_COURSES, 90)
    raise NotImplementedError("Real Coursera API integration not configured.")


def fetch_hackathons() -> list:
    if settings.opportunities_are_mocked:
        return _attach_deadlines(MOCK_HACKATHONS, 14)
    raise NotImplementedError("Real hackathon source integration not configured.")
