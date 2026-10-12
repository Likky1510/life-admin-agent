from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import get_settings

settings = get_settings()

def _resolve_database_url(database_url: str) -> str:
    if not database_url.startswith("sqlite"):
        return database_url
    if database_url.startswith("sqlite:///"):
        raw_path = database_url[len("sqlite:///"):]
        if raw_path.startswith("/"):
            return database_url
        if not Path(raw_path).is_absolute():
            backend_dir = Path(__file__).resolve().parents[2]
            resolved_path = (backend_dir / raw_path).resolve()
            return f"sqlite:///{resolved_path}"
    return database_url


connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
engine = create_engine(_resolve_database_url(settings.database_url), pool_pre_ping=True, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
