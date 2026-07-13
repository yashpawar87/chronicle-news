"""Fetch scheduler — runs the fetch manager on a recurring cadence.

Uses APScheduler to trigger fetch cycles every N minutes (configurable).
This runs independently of the rewrite pipeline.
"""

from __future__ import annotations

import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.config import settings
from app.db.session import async_session_factory
from app.fetchers.manager import run_fetch_cycle

logger = logging.getLogger(__name__)

_scheduler: AsyncIOScheduler | None = None


async def _fetch_job():
    """The scheduled job that runs a fetch cycle."""
    logger.info("Scheduled fetch cycle starting...")
    async with async_session_factory() as session:
        try:
            summary = await run_fetch_cycle(
                session, config_path=settings.sources_yaml_path
            )
            await session.commit()
            logger.info("Scheduled fetch cycle complete: %s", summary)
        except Exception as e:
            await session.rollback()
            logger.error("Scheduled fetch cycle failed: %s", e)


def start_fetch_scheduler() -> AsyncIOScheduler:
    """Start the APScheduler for periodic fetching."""
    global _scheduler

    _scheduler = AsyncIOScheduler()
    _scheduler.add_job(
        _fetch_job,
        "interval",
        minutes=settings.fetch_interval_minutes,
        id="fetch_cycle",
        name="Periodic news fetch",
        replace_existing=True,
    )
    _scheduler.start()
    logger.info(
        "Fetch scheduler started — running every %d minutes",
        settings.fetch_interval_minutes,
    )
    return _scheduler


def stop_fetch_scheduler():
    """Stop the fetch scheduler gracefully."""
    global _scheduler
    if _scheduler and _scheduler.running:
        _scheduler.shutdown(wait=False)
        logger.info("Fetch scheduler stopped")
        _scheduler = None
