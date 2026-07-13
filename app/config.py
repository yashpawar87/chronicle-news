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

    # ── Security ────────────────────────────────────────────────────────
    cors_allowed_origins: str = ""

    # ── Fetcher ──────────────────────────────────────────────────────────
    sources_yaml_path: str = "app/fetchers/sources.yaml"
    fetch_news_timezone: str = "Asia/Kolkata"

    @model_validator(mode="after")
    def apply_environment_defaults(self) -> "Settings":
        """Keep development easy, but force explicit secrets in production."""
        if self.app_env == "development":
            if not self.cors_allowed_origins:
                self.cors_allowed_origins = (
                    "http://localhost:3000,"
                    "http://127.0.0.1:3000,"
                    "http://localhost:8080,"
                    "http://127.0.0.1:8080"
                )
            return self

        missing = []
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
