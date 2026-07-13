"""Fetch Manager — the single gatekeeper between fetchers and storage.

Responsibilities:
  1. Load sources from YAML config.
  2. Instantiate the right fetcher type for each source.
  3. Run all fetchers concurrently.
  4. Validate, deduplicate, and persist raw stories to the DB.

Fetchers never write to the DB directly — the manager owns that path.
"""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional
from zoneinfo import ZoneInfo

import yaml
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.db.models import RawStory, Source
from app.fetchers.base import Fetcher, RawStorySchema
from app.fetchers.extractors.trafilatura_extractor import extract_article
from app.fetchers.rss.rss_fetcher import RSSFetcher

logger = logging.getLogger(__name__)

# Mapping from source type string → fetcher class
FETCHER_TYPES: dict[str, type[Fetcher]] = {
    "rss": RSSFetcher,
}

_FETCH_CYCLE_LOCK = asyncio.Lock()


class FetchCycleBusyError(RuntimeError):
    """Raised when a fetch cycle is already running."""


def _is_story_from_today(story: RawStorySchema) -> bool:
    """Keep only stories published on the current day in the configured timezone."""
    if story.published_at is None:
        return False

    tz = ZoneInfo(settings.fetch_news_timezone)
    published = story.published_at
    if published.tzinfo is None:
        published = published.replace(tzinfo=timezone.utc)

    today_local = datetime.now(tz).date()
    published_local = published.astimezone(tz).date()
    return published_local == today_local


def load_fetchers_from_config(config_path: str) -> list[Fetcher]:
    """Load the sources YAML and instantiate one fetcher per source entry.

    Args:
        config_path: Path to the sources.yaml file.

    Returns:
        A list of Fetcher instances ready to call .fetch().
    """
    path = Path(config_path)
    if not path.exists():
        logger.error("Sources config not found: %s", config_path)
        return []

    with open(path, "r") as f:
        config = yaml.safe_load(f)

    sources = config.get("sources", [])
    fetchers: list[Fetcher] = []

    for entry in sources:
        name = entry.get("name")
        source_type = entry.get("type", "rss")
        url = entry.get("url")

        fetcher_cls = FETCHER_TYPES.get(source_type)
        if not fetcher_cls:
            logger.warning(
                "Unknown fetcher type '%s' for source '%s' — skipping",
                source_type,
                name,
            )
            continue

        kwargs: dict = {
            "source_name": name,
            "feed_url": url,
            "extract_full_text": False,
        }

        try:
            fetcher = fetcher_cls(**kwargs)
            fetchers.append(fetcher)
        except Exception as e:
            logger.error("Failed to create fetcher for '%s': %s", name, e)

    logger.info("Loaded %d fetchers from config", len(fetchers))
    return fetchers


async def _ensure_source_exists(
    session: AsyncSession, source_name: str, feed_url: Optional[str] = None
) -> Source:
    """Get or create a Source record."""
    result = await session.execute(
        select(Source).where(Source.name == source_name)
    )
    source = result.scalar_one_or_none()
    if source is None:
        source = Source(
            name=source_name,
            feed_url=feed_url,
            source_type="rss",
        )
        session.add(source)
        await session.flush()
    elif feed_url and source.feed_url != feed_url:
        source.feed_url = feed_url
    return source


async def _is_duplicate(
    session: AsyncSession,
    url: str,
    title: str,
    source_id: int,
) -> bool:
    """Check if this story is a duplicate.

    Duplicate rules:
      1. Exact URL already exists → duplicate.
      2. Same/near-identical title from the same source within 24h → duplicate.
    """
    # Check exact URL
    result = await session.execute(
        select(RawStory.id).where(RawStory.url == url).limit(1)
    )
    if result.scalar_one_or_none() is not None:
        return True

    # Check same title from same source within 24h
    cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
    result = await session.execute(
        select(RawStory.id)
        .where(
            RawStory.source_id == source_id,
            RawStory.title == title,
            RawStory.fetched_at >= cutoff,
        )
        .limit(1)
    )
    if result.scalar_one_or_none() is not None:
        return True

    return False


async def _extract_story_content(url: str) -> str | None:
    """Fetch full article text only for stories that already passed filtering."""
    try:
        return await extract_article(url)
    except Exception as e:
        logger.debug("Could not extract full text for %s: %s", url, e)
        return None


async def run_fetch_cycle(
    session: AsyncSession,
    config_path: str = "app/fetchers/sources.yaml",
) -> dict:
    """Run a complete fetch cycle: load config → fetch all → dedup → persist.

    Args:
        session: An async DB session.
        config_path: Path to the sources.yaml config.

    Returns:
        A summary dict with counts.
    """
    if _FETCH_CYCLE_LOCK.locked():
        raise FetchCycleBusyError("A fetch cycle is already running")

    async with _FETCH_CYCLE_LOCK:
        fetchers = load_fetchers_from_config(config_path)

        if not fetchers:
            logger.warning("No fetchers loaded — nothing to fetch")
            return {"fetched": 0, "new": 0, "duplicates": 0, "errors": 0}

        # Run all fetchers concurrently
        logger.info("Starting fetch cycle with %d fetchers...", len(fetchers))
        results = await asyncio.gather(
            *[f.fetch() for f in fetchers],
            return_exceptions=True,
        )

        # Collect all stories
        all_stories: list[RawStorySchema] = []
        errors = 0
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(
                    "Fetcher '%s' raised: %s",
                    fetchers[i].source_name,
                    result,
                )
                errors += 1
            elif isinstance(result, list):
                all_stories.extend(result)

        logger.info(
            "Collected %d stories from %d fetchers", len(all_stories), len(fetchers)
        )

        # Deduplicate and persist
        new_count = 0
        dup_count = 0
        skipped_old = 0

        for story in all_stories:
            try:
                if not _is_story_from_today(story):
                    skipped_old += 1
                    continue

                source = await _ensure_source_exists(session, story.source_name)

                if await _is_duplicate(session, story.url, story.title, source.id):
                    dup_count += 1
                    continue

                content = story.content
                if content is None:
                    content = await _extract_story_content(story.url)

                raw_story = RawStory(
                    source_id=source.id,
                    title=story.title,
                    summary=story.summary,
                    url=story.url,
                    content=content,
                    image_url=story.image_url,
                    published_at=story.published_at,
                )
                session.add(raw_story)
                new_count += 1

            except Exception as e:
                logger.warning("Failed to persist story '%s': %s", story.title[:50], e)
                errors += 1

        await session.flush()

        summary = {
            "fetched": len(all_stories),
            "new": new_count,
            "duplicates": dup_count,
            "skipped_not_today": skipped_old,
            "errors": errors,
        }
        logger.info(
            "Fetch cycle complete: %d fetched, %d new, %d duplicates, %d skipped as not-today, %d errors",
            summary["fetched"],
            summary["new"],
            summary["duplicates"],
            summary["skipped_not_today"],
            summary["errors"],
        )
        return summary
