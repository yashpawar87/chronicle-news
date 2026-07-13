"""SQLAlchemy 2.0 ORM models for the RSS reader."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Base class for all models."""

    pass


# ── Models ───────────────────────────────────────────────────────────────


class Source(Base):
    """A news publisher / feed source."""

    __tablename__ = "sources"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    base_url: Mapped[str | None] = mapped_column(String(1024))
    feed_url: Mapped[str | None] = mapped_column(String(1024))
    source_type: Mapped[str] = mapped_column(
        String(50), nullable=False, default="rss"
    )  # rss
    trust_weight: Mapped[float] = mapped_column(Float, default=1.0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    raw_stories: Mapped[list[RawStory]] = relationship(back_populates="source")


class RawStory(Base):
    """A single fetched story from a source, before clustering/rewriting."""

    __tablename__ = "raw_stories"
    __table_args__ = (
        UniqueConstraint("url", name="uq_raw_stories_url"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    source_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("sources.id"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(1024), nullable=False)
    summary: Mapped[str | None] = mapped_column(Text)
    url: Mapped[str] = mapped_column(String(2048), nullable=False)
    content: Mapped[str | None] = mapped_column(Text)  # Full extracted article text
    image_url: Mapped[str | None] = mapped_column(String(2048))
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    fetched_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    source: Mapped[Source] = relationship(back_populates="raw_stories")
