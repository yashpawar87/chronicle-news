"""Admin API routes — dev/testing tools.

POST /admin/run-fetch  — Manually trigger a fetch cycle
GET  /admin/stats      — Database statistics
"""

from __future__ import annotations

import logging
import time
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.db.models import RawStory, Source
from app.db.session import get_db
from app.fetchers.manager import FetchCycleBusyError

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin", tags=["admin"])

_LAST_FETCH_STARTED_AT = 0.0


async def require_admin_token(x_admin_token: str = Header(default="")) -> None:
    """Require a shared admin token for admin endpoints."""
    if not settings.admin_api_token or x_admin_token != settings.admin_api_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid admin token",
        )


@router.post("/run-fetch")
async def run_fetch(
    _: None = Depends(require_admin_token),
    db: AsyncSession = Depends(get_db),
):
    """Manually trigger a fetch cycle (fetch only, no rewriting)."""
    from app.fetchers.manager import run_fetch_cycle

    global _LAST_FETCH_STARTED_AT
    now = time.monotonic()
    if now - _LAST_FETCH_STARTED_AT < settings.admin_fetch_cooldown_seconds:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Admin fetch is temporarily rate-limited",
        )
    _LAST_FETCH_STARTED_AT = now

    try:
        results = await run_fetch_cycle(db)
        return {
            "status": "completed",
            "results": results,
            "message": "Fetch cycle completed",
            "completed_at": datetime.now(timezone.utc).isoformat(),
        }
    except FetchCycleBusyError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A fetch cycle is already running",
        )
    except Exception as e:
        logger.error("Fetch cycle failed: %s", e)
        raise HTTPException(
            status_code=500,
            detail="Fetch cycle failed",
        ) from e


@router.get("/stats")
async def get_stats(
    _: None = Depends(require_admin_token),
    db: AsyncSession = Depends(get_db),
):
    """Get database statistics for monitoring."""
    raw_count = await db.scalar(select(func.count(RawStory.id)))
    source_count = await db.scalar(select(func.count(Source.id)))

    return {
        "raw_stories": raw_count or 0,
        "sources": source_count or 0,
        "checked_at": datetime.now(timezone.utc).isoformat(),
    }
