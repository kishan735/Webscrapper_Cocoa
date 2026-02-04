"""Configuration settings for the Cocoa Price Tracker."""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # AI API Keys (in order of preference - all have FREE tiers!)
    groq_api_key: str = ""  # FREE: https://console.groq.com/keys
    gemini_api_key: str = ""  # FREE: https://aistudio.google.com/apikey
    huggingface_api_key: str = ""  # FREE: https://huggingface.co/settings/tokens
    openai_api_key: str = ""  # Paid fallback

    # Database
    database_url: str = "sqlite+aiosqlite:///./data/cocoa_tracker.db"

    # Scraper Settings
    scrape_interval_minutes: int = 30
    news_fetch_limit: int = 50

    # App Settings
    app_name: str = "Cocoa Price Tracker"
    debug: bool = True

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
