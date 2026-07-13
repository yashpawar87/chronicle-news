"""Shared test fixtures for pytest."""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.db.models import Base, Source, RawStory


# Use a separate test database
TEST_DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/newspaper_ai_test"


@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for the test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def engine():
    """Create a test database engine."""
    eng = create_async_engine(TEST_DATABASE_URL, echo=False)

    # Create all tables
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    yield eng

    # Cleanup
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await eng.dispose()


@pytest_asyncio.fixture
async def db_session(engine):
    """Provide a transactional test DB session that rolls back after each test."""
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
async def sample_source(db_session: AsyncSession) -> Source:
    """Create a sample source for testing."""
    source = Source(
        name="Test Source",
        base_url="https://test.example.com",
        feed_url="https://test.example.com/rss",
        source_type="rss",
        trust_weight=1.0,
    )
    db_session.add(source)
    await db_session.flush()
    return source


@pytest_asyncio.fixture
async def sample_stories(db_session: AsyncSession, sample_source: Source) -> list[RawStory]:
    """Create sample raw stories for testing."""
    stories = [
        RawStory(
            source_id=sample_source.id,
            title="India launches new space mission to study the Sun",
            summary="ISRO confirmed plans for Aditya-L2 mission",
            url="https://test.example.com/article/1",
            content="India's space agency ISRO announced a new solar mission...",
            published_at=datetime.now(timezone.utc),
        ),
        RawStory(
            source_id=sample_source.id,
            title="ISRO announces solar observation mission Aditya-L2",
            summary="Indian Space Research Organisation plans Sun study",
            url="https://test.example.com/article/2",
            content="The Indian Space Research Organisation has unveiled plans...",
            published_at=datetime.now(timezone.utc),
        ),
        RawStory(
            source_id=sample_source.id,
            title="Cricket: India wins test series against Australia",
            summary="India clinched the Border-Gavaskar Trophy",
            url="https://test.example.com/article/3",
            content="India secured a historic test series victory...",
            published_at=datetime.now(timezone.utc),
        ),
    ]
    for story in stories:
        db_session.add(story)
    await db_session.flush()
    return stories


@pytest_asyncio.fixture
async def test_client():
    """Create a test HTTP client for the FastAPI app."""
    from app.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        yield client
