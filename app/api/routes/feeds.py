"""RSS feed API routes for the simple sectioned frontend.

GET /feeds/sections  -- grouped RSS stories by configured source
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

import yaml
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.config import settings
from app.db.models import Source
from app.db.session import get_db
from pydantic import BaseModel, Field
from sqlalchemy.orm import selectinload

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
async def get_sections(db: AsyncSession = Depends(get_db)):
    """Return grouped RSS stories for the frontend."""
    config_entries = _load_section_config()
    section_order = [entry.get("name", "Untitled") for entry in config_entries]
    feed_urls = {entry.get("name", "Untitled"): entry.get("url") for entry in config_entries}

    result = await db.execute(
        select(Source)
        .options(selectinload(Source.raw_stories))
        .order_by(Source.name.asc())
    )
    sources = result.scalars().unique().all()

    source_map = {source.name: source for source in sources}
    sections: list[FeedSectionResponse] = []

    for section_name in section_order:
        source = source_map.get(section_name)
        if not source:
            sections.append(
                FeedSectionResponse(
                    section=section_name,
                    feed_url=feed_urls.get(section_name),
                    stories=[],
                )
            )
            continue

        stories = sorted(
            source.raw_stories,
            key=lambda story: story.published_at or story.fetched_at,
            reverse=True,
        )
        sections.append(
            FeedSectionResponse(
                section=section_name,
                feed_url=source.feed_url or feed_urls.get(section_name),
                stories=[
                    FeedStory(
                        id=story.id,
                        title=story.title,
                        summary=story.summary,
                        url=story.url,
                        image_url=story.image_url,
                        published_at=story.published_at,
                        source_name=source.name,
                    )
                    for story in stories[:8]
                ],
            )
        )

    return sections
