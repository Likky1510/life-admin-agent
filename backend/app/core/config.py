"""
Central configuration. Reads from .env (see .env.example).
Every external integration has a "mock" mode so the full app runs
end-to-end before you have any real credentials.
"""
from pathlib import Path
from pydantic import model_validator
from pydantic_settings import BaseSettings
from functools import lru_cache


BACKEND_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    database_url: str = f"sqlite:///{(BACKEND_DIR / 'life_admin.db').resolve()}"

    jwt_secret_key: str = "dev-secret-change-me"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 1440

    anthropic_api_key: str = "mock"
    claude_model: str = "claude-sonnet-4-6"

    opportunity_source_mode: str = "mock"

    smtp_mode: str = "mock"
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    smtp_from_email: str = "noreply@example.com"

    firebase_mode: str = "mock"
    firebase_server_key: str = ""

    google_calendar_mode: str = "mock"
    google_calendar_credentials_json: str = ""

    chroma_persist_dir: str = "./chroma_data"

    environment: str = "development"

    class Config:
        env_file = str(BACKEND_DIR / ".env")
        env_file_encoding = "utf-8"

    @model_validator(mode="after")
    def normalize_database_path(self):
        if self.database_url.startswith("sqlite:///./"):
            relative_path = self.database_url[len("sqlite:///./"):]
            self.database_url = f"sqlite:///{(BACKEND_DIR / relative_path).resolve()}"
        elif self.database_url.startswith("sqlite://./"):
            relative_path = self.database_url[len("sqlite://./"):]
            self.database_url = f"sqlite:///{(BACKEND_DIR / relative_path).resolve()}"
        return self

    @property
    def claude_is_mocked(self) -> bool:
        return self.anthropic_api_key.lower() == "mock"

    @property
    def opportunities_are_mocked(self) -> bool:
        return self.opportunity_source_mode.lower() == "mock"

    @property
    def smtp_is_mocked(self) -> bool:
        return self.smtp_mode.lower() == "mock"

    @property
    def firebase_is_mocked(self) -> bool:
        return self.firebase_mode.lower() == "mock"

    @property
    def calendar_is_mocked(self) -> bool:
        return self.google_calendar_mode.lower() == "mock"


@lru_cache
def get_settings() -> Settings:
    return Settings()
