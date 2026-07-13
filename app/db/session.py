"""SQLAlchemy async engine and session management."""

from __future__ import annotations

from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.config import settings


def _normalize_database_url(url: str) -> tuple[str, dict[str, object]]:
    """Convert common Postgres URLs into asyncpg form and map SSL settings."""
    parsed = make_url(url)
    connect_args: dict[str, object] = {}

    if parsed.drivername in {"postgresql", "postgres"}:
        parsed = parsed.set(drivername="postgresql+asyncpg")

    query = dict(parsed.query)
    sslmode = query.pop("sslmode", None)
    if sslmode is not None:
        parsed = parsed.set(query=query)
        if sslmode in {"require", "verify-ca", "verify-full"}:
            connect_args["ssl"] = True

    return str(parsed), connect_args

DATABASE_URL, CONNECT_ARGS = _normalize_database_url(settings.database_url)

engine = create_async_engine(
    DATABASE_URL,
    connect_args=CONNECT_ARGS,
    echo=(settings.app_env == "development"),
    pool_size=5,
    max_overflow=10,
)

async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncSession:
    """FastAPI dependency that yields an async DB session."""
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """Create all tables for local development and testing."""
    from app.db.models import Base

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db() -> None:
    """Dispose the engine connection pool."""
    await engine.dispose()
