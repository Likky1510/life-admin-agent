"""
Main FastAPI app. Run with:
  uvicorn app.main:app --reload
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db.session import engine, Base
from app.routers import auth, life_items, notifications, opportunities, assistant, analytics
from app.core.scheduler import start_scheduler, stop_scheduler

logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    start_scheduler()
    yield
    stop_scheduler()


app = FastAPI(
    title="Autonomous Life Admin & Opportunity Discovery Agent",
    description="Multi-agent personal assistant: life admin, reminders, opportunity discovery, AI chat, and analytics.",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(life_items.router)
app.include_router(notifications.router)
app.include_router(opportunities.router)
app.include_router(assistant.router)
app.include_router(analytics.router)


@app.get("/health")
def health_check():
    return {"status": "ok"}
