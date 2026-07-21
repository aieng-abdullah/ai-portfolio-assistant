import os
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql://portfolio:portfolio_dev@localhost:5432/portfolio"
    )
    n8n_webhook_url: str = os.getenv(
        "N8N_WEBHOOK_URL",
        "http://localhost:5678/webhook/"
    )
    google_oauth_client_id: str = os.getenv("GOOGLE_OAUTH_CLIENT_ID", "")
    google_oauth_client_secret: str = os.getenv("GOOGLE_OAUTH_CLIENT_SECRET", "")
    groq_api_key: str = os.getenv("GROQ_API_KEY", "")

    class Config:
        env_file = ".env"
        extra = "allow"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
