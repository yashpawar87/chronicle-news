"""Base classes and schemas for the fetcher subsystem.

Every fetcher — regardless of transport (RSS, API, scraper) — implements the
Fetcher ABC and returns a list[RawStorySchema].  The rest of the pipeline
never needs to know *how* a story was obtained.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class RawStorySchema(BaseModel):
    """Normalized shape for a single fetched story.

    This is a *transport* schema — it's what fetchers produce before the
    story is persisted to the DB.
    """

    title: str
    summary: Optional[str] = None
    url: str
    source_name: str  # Human-readable publisher name (e.g., "Reuters")
    published_at: Optional[datetime] = None
    image_url: Optional[str] = None
    content: Optional[str] = None  # Full extracted article text (may be None)

    class Config:
        json_schema_extra = {
            "example": {
                "title": "India announces new space mission",
                "summary": "ISRO confirmed plans for...",
                "url": "https://example.com/article/123",
                "source_name": "The Hindu",
                "published_at": "2026-07-08T10:00:00Z",
                "image_url": "https://example.com/img.jpg",
                "content": "Full article text here...",
            }
        }


class Fetcher(ABC):
    """Abstract base class for all fetcher types.

    Subclasses must implement `fetch()` which returns a list of
    RawStorySchema objects.  The FetchManager calls this method and
    handles validation, dedup, and persistence.
    """

    def __init__(self, source_name: str, **kwargs):
        self.source_name = source_name

    @abstractmethod
    async def fetch(self) -> list[RawStorySchema]:
        """Fetch stories from this source.

        Returns a list of normalized RawStorySchema objects.
        Should handle its own errors gracefully (log and return partial
        results rather than crashing the whole fetch cycle).
        """
        ...
