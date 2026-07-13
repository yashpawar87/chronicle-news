"""Generic RSS/Atom fetcher — reusable across all publishers.

Given a feed URL and a source name, this fetcher:
  1. Downloads and parses the RSS/Atom feed via feedparser.
  2. Extracts title, summary, link, published date, and image from each entry.
  3. Optionally extracts full article text via trafilatura.
  4. Returns a list[RawStorySchema].
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from typing import Optional

import feedparser
import httpx

from app.fetchers.base import Fetcher, RawStorySchema
from app.fetchers.extractors.trafilatura_extractor import extract_article

logger = logging.getLogger(__name__)


class RSSFetcher(Fetcher):
    """A generic, reusable RSS/Atom feed fetcher."""

    def __init__(
        self,
        source_name: str,
        feed_url: str,
        extract_full_text: bool = True,
        timeout: float = 30.0,
    ):
        super().__init__(source_name)
        self.feed_url = feed_url
        self.extract_full_text = extract_full_text
        self.timeout = timeout

    async def fetch(self) -> list[RawStorySchema]:
        """Fetch and parse the RSS feed, returning normalized stories."""
        stories: list[RawStorySchema] = []

        try:
            # Download the feed
            async with httpx.AsyncClient(
                timeout=self.timeout, follow_redirects=True
            ) as client:
                response = await client.get(self.feed_url, headers={
                    "User-Agent": "NewspaperAI/1.0 (RSS Reader)"
                })
                response.raise_for_status()

            feed = feedparser.parse(response.text)

            if feed.bozo and not feed.entries:
                logger.warning(
                    "Feed parse error for %s (%s): %s",
                    self.source_name,
                    self.feed_url,
                    feed.bozo_exception,
                )
                return stories

            logger.info(
                "Fetched %d entries from %s", len(feed.entries), self.source_name
            )

            for entry in feed.entries:
                try:
                    story = await self._parse_entry(entry)
                    if story:
                        stories.append(story)
                except Exception as e:
                    logger.warning(
                        "Failed to parse entry from %s: %s",
                        self.source_name,
                        e,
                    )
                    continue

        except httpx.HTTPError as e:
            logger.error(
                "HTTP error fetching %s (%s): %s",
                self.source_name,
                self.feed_url,
                e,
            )
        except Exception as e:
            logger.error(
                "Unexpected error fetching %s: %s", self.source_name, e
            )

        return stories

    async def _parse_entry(self, entry) -> Optional[RawStorySchema]:
        """Parse a single feed entry into a RawStorySchema."""
        # URL is required
        url = getattr(entry, "link", None)
        if not url:
            return None

        title = getattr(entry, "title", "").strip()
        if not title:
            return None

        # Summary
        summary = getattr(entry, "summary", None)
        if summary:
            # Strip HTML tags from summary
            import re
            summary = re.sub(r"<[^>]+>", "", summary).strip()

        # Published date
        published_at = self._parse_date(entry)

        # Image URL — check media_content, media_thumbnail, enclosures
        image_url = self._extract_image(entry)

        # Full text extraction (optional, can be slow)
        content = None
        if self.extract_full_text:
            try:
                content = await extract_article(url)
            except Exception as e:
                logger.debug(
                    "Could not extract full text for %s: %s", url, e
                )

        return RawStorySchema(
            title=title,
            summary=summary,
            url=url,
            source_name=self.source_name,
            published_at=published_at,
            image_url=image_url,
            content=content,
        )

    @staticmethod
    def _parse_date(entry) -> Optional[datetime]:
        """Try to parse a datetime from the entry."""
        # feedparser provides published_parsed or updated_parsed
        for attr in ("published_parsed", "updated_parsed"):
            parsed = getattr(entry, attr, None)
            if parsed:
                try:
                    from calendar import timegm
                    return datetime.fromtimestamp(timegm(parsed), tz=timezone.utc)
                except Exception:
                    pass

        # Try raw string
        for attr in ("published", "updated"):
            raw = getattr(entry, attr, None)
            if raw:
                try:
                    parsed_dt = parsedate_to_datetime(raw)
                    if parsed_dt.tzinfo is None:
                        return parsed_dt.replace(tzinfo=timezone.utc)
                    return parsed_dt.astimezone(timezone.utc)
                except Exception:
                    pass

        return None

    @staticmethod
    def _extract_image(entry) -> Optional[str]:
        """Try to find an image URL in the feed entry."""
        # media:content
        media_content = getattr(entry, "media_content", None)
        if media_content:
            for media in media_content:
                url = media.get("url", "")
                media_type = media.get("type", "")
                if url and ("image" in media_type or url.endswith(
                    (".jpg", ".jpeg", ".png", ".webp")
                )):
                    return url

        # media:thumbnail
        media_thumbnail = getattr(entry, "media_thumbnail", None)
        if media_thumbnail:
            for thumb in media_thumbnail:
                url = thumb.get("url", "")
                if url:
                    return url

        # Enclosures
        enclosures = getattr(entry, "enclosures", [])
        for enc in enclosures:
            enc_type = enc.get("type", "")
            if "image" in enc_type:
                return enc.get("href") or enc.get("url")

        return None
