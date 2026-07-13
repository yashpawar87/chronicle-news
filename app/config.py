"""Application configuration via pydantic-settings.

All settings are loaded from environment variables or a .env file.
"""

from __future__ import annotations

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central configuration for the AI Editor-in-Chief backend."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Runtime ───────────────────────────────────────────────────────────
    app_env: str = "development"
    log_level: str = "INFO"

    # ── Database / Security ─────────────────────────────────────────────
    database_url: str | None = None
    admin_api_token: str | None = None
    cors_allowed_origins: str = ""

    # ── Fetcher ──────────────────────────────────────────────────────────
    fetch_interval_minutes: int = 10
    sources_yaml_path: str = "app/fetchers/sources.yaml"
    fetch_news_timezone: str = "Asia/Kolkata"

    admin_fetch_cooldown_seconds: int = 300

    @model_validator(mode="after")
    def apply_environment_defaults(self) -> "Settings":
        """Keep development easy, but force explicit secrets in production."""
        if self.app_env == "development":
            if not self.database_url:
                self.database_url = (
                    "postgresql+asyncpg://postgres:postgres@localhost:5432/newspaper_ai"
                )
            if not self.admin_api_token:
                self.admin_api_token = "dev-admin-token"
            if not self.cors_allowed_origins:
                self.cors_allowed_origins = (
                    "http://localhost:3000,"
                    "http://127.0.0.1:3000,"
                    "http://localhost:8080,"
                    "http://127.0.0.1:8080"
                )
            return self

        missing = []
        if not self.database_url:
            missing.append("DATABASE_URL")
        if not self.admin_api_token:
            missing.append("ADMIN_API_TOKEN")
        if not self.cors_allowed_origins:
            missing.append("CORS_ALLOWED_ORIGINS")
        if missing:
            joined = ", ".join(missing)
            raise ValueError(f"Missing required production settings: {joined}")

        return self

    @property
    def allowed_origins(self) -> list[str]:
        return [origin.strip() for origin in self.cors_allowed_origins.split(",") if origin.strip()]


settings = Settings()
