"""Application configuration via environment variables."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration loaded from .env or environment."""

    database_url: str = "sqlite:///./cobalt_lab.db"
    host: str = "127.0.0.1"
    port: int = 8000

    # LLM provider settings (optional — engine works offline without these)
    llm_api_key: str | None = None
    llm_provider: str | None = None
    llm_model: str | None = None
    llm_base_url: str | None = None

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()