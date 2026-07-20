import os
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    database_url: str = os.getenv(
        "DATABASE_URL",
        "sqlite:///./portfolio.db"
    )
    n8n_webhook_url: str = os.getenv(
        "N8N_WEBHOOK_URL",
        "http://localhost:5678/webhook/"
    )
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    groq_api_key: str = os.getenv("GROQ_API_KEY", "")
    api_host: str = os.getenv("API_HOST", "0.0.0.0")
    api_port: int = int(os.getenv("API_PORT", "3000"))
    environment: str = os.getenv("ENVIRONMENT", "development")
    google_oauth_client_id: str = os.getenv("GOOGLE_OAUTH_CLIENT_ID", "")
    google_oauth_client_secret: str = os.getenv("GOOGLE_OAUTH_CLIENT_SECRET", "")

    class Config:
        env_file = ".env"
        extra = "allow"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
