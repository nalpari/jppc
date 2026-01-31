"""Application configuration module."""

from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Application
    app_name: str = "Japan Power Price Crawler"
    app_version: str = "0.1.0"
    debug: bool = False
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"

    # Database
    database_url: str = "postgresql+asyncpg://jppc:jppc_password@localhost:5432/jppc_db"
    database_url_sync: str = "postgresql://jppc:jppc_password@localhost:5432/jppc_db"

    # SMTP Configuration
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from: str = "noreply@jppc.local"
    smtp_use_tls: bool = True

    # Crawler Configuration
    crawler_timeout: int = 60  # seconds
    crawler_retry_count: int = 3
    crawler_retry_delay: int = 5  # seconds
    crawler_user_agent: str = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )

    # Scheduler Configuration
    scheduler_enabled: bool = True
    default_crawl_day: int = 1  # Monday (0=Sunday, 1=Monday, ...)
    default_crawl_hour: int = 2  # 2 AM


@lru_cache
def get_settings() -> Settings:
    """Get cached application settings."""
    return Settings()
