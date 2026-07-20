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
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    groq_api_key: str = os.getenv("GROQ_API_KEY", "")
    api_host: str = os.getenv("API_HOST", "0.0.0.0")
    api_port: int = int(os.getenv("API_PORT", "3000"))
    environment: str = os.getenv("ENVIRONMENT", "development")

    class Config:
        env_file = ".env"
        extra = "allow"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
