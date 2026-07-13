"""Pydantic v2 response schemas for the RSS backend."""

from __future__ import annotations

from pydantic import BaseModel


class HealthResponse(BaseModel):
    """Response for GET /health."""

    status: str = "ok"
    version: str = "1.0.0"
    environment: str = "development"
