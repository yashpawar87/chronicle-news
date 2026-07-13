"""RSS feed API routes for the simple sectioned frontend.

GET /feeds/sections  -- grouped RSS stories by configured source
"""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime
from pathlib import Path

import yaml
from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.config import settings
from app.fetchers.rss.rss_fetcher import RSSFetcher

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/feeds", tags=["feeds"])


class FeedStory(BaseModel):
    id: int
    title: str
    summary: str | None = None
    url: str
    image_url: str | None = None
    published_at: datetime | None = None
    source_name: str


class FeedSectionResponse(BaseModel):
    section: str
    feed_url: str | None = None
    stories: list[FeedStory] = Field(default_factory=list)


def _load_section_config() -> list[dict]:
    path = Path(settings.sources_yaml_path)
    if not path.exists():
        return []

    with open(path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f) or {}

    return config.get("sources", [])


@router.get("/sections", response_model=list[FeedSectionResponse])
async def get_sections():
    """Return live grouped RSS stories for the frontend."""
    config_entries = _load_section_config()
    
    fetchers = []
    for entry in config_entries:
        source_type = entry.get("type", "rss")
        name = entry.get("name", "Untitled")
        url = entry.get("url")
        
        if source_type == "rss" and url:
            # extract_full_text=False to speed up live API
            fetchers.append(RSSFetcher(source_name=name, feed_url=url, extract_full_text=False))

    logger.info("Fetching live RSS for %d sources...", len(fetchers))
    
    results = await asyncio.gather(
        *[f.fetch() for f in fetchers],
        return_exceptions=True
    )
    
    sections: list[FeedSectionResponse] = []
    
    fake_id = 1
    
    for idx, entry in enumerate(config_entries):
        section_name = entry.get("name", "Untitled")
        feed_url = entry.get("url")
        
        stories_in_section = []
        if idx < len(results):
            result = results[idx]
            if not isinstance(result, Exception):
                for story in result[:8]:
                    stories_in_section.append(
                        FeedStory(
                            id=fake_id,
                            title=story.title,
                            summary=story.summary,
                            url=story.url,
                            image_url=story.image_url,
                            published_at=story.published_at,
                            source_name=story.source_name,
                        )
                    )
                    fake_id += 1
            else:
                logger.error("Error fetching %s: %s", section_name, result)
                
        sections.append(
            FeedSectionResponse(
                section=section_name,
                feed_url=feed_url,
                stories=stories_in_section,
            )
        )

    return sections
