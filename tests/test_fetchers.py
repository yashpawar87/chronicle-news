"""Tests for the RSS fetcher subsystem."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from app.fetchers.base import Fetcher, RawStorySchema
from app.fetchers.manager import _is_story_from_today
from app.fetchers.rss.rss_fetcher import RSSFetcher


class TestRawStorySchema:
    """Test the RawStorySchema validation."""

    def test_valid_story(self):
        story = RawStorySchema(
            title="Test headline",
            summary="Test summary",
            url="https://example.com/article",
            source_name="Test Source",
        )
        assert story.title == "Test headline"
        assert story.url == "https://example.com/article"
        assert story.source_name == "Test Source"
        assert story.content is None


class TestFetcherABC:
    """Test that the Fetcher ABC enforces its contract."""

    def test_cannot_instantiate_abc(self):
        with pytest.raises(TypeError):
            Fetcher(source_name="test")

    def test_subclass_must_implement_fetch(self):
        class IncompleteFetcher(Fetcher):
            pass

        with pytest.raises(TypeError):
            IncompleteFetcher(source_name="test")

    def test_valid_subclass(self):
        class ValidFetcher(Fetcher):
            async def fetch(self):
                return []

        fetcher = ValidFetcher(source_name="test")
        assert fetcher.source_name == "test"


class TestFetcherConfig:
    """Test loading fetchers from YAML config."""

    def test_load_from_config(self):
        from app.fetchers.manager import load_fetchers_from_config

        fetchers = load_fetchers_from_config("app/fetchers/sources.yaml")
        assert len(fetchers) > 0
        for fetcher in fetchers:
            assert fetcher.source_name


class TestTodayFilter:
    """Test filtering stories to today's local date."""

    def test_story_from_today_is_kept(self):
        story = RawStorySchema(
            title="Today story",
            url="https://example.com/today",
            source_name="Test Source",
            published_at=datetime.now(timezone.utc),
        )
        assert _is_story_from_today(story) is True

    def test_story_from_previous_day_is_skipped(self):
        story = RawStorySchema(
            title="Old story",
            url="https://example.com/old",
            source_name="Test Source",
            published_at=datetime.now(timezone.utc) - timedelta(days=2),
        )
        assert _is_story_from_today(story) is False

    def test_story_without_publish_time_is_skipped(self):
        story = RawStorySchema(
            title="Undated story",
            url="https://example.com/undated",
            source_name="Test Source",
        )
        assert _is_story_from_today(story) is False


class TestRssDateParsing:
    """Test RSS date parsing with timezone-aware pubDate strings."""

    def test_pubdate_with_offset_is_converted_to_utc(self):
        class Entry:
            published = "Thu, 09 Jul 2026 02:07:44 +0530"

        parsed = RSSFetcher._parse_date(Entry())
        assert parsed is not None
        assert parsed.tzinfo == timezone.utc
        assert parsed.isoformat() == "2026-07-08T20:37:44+00:00"
