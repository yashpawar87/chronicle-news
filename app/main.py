"""FastAPI application entrypoint for the RSS backend.

Registers all routes, sets up DB lifecycle, and starts the fetch scheduler.
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.schemas import HealthResponse
from app.config import settings

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan — startup and shutdown hooks."""
    from app.db.session import init_db, close_db
    from app.fetchers.scheduler import start_fetch_scheduler, stop_fetch_scheduler

    # ── Startup ──────────────────────────────────────────────────────
    logger.info("Starting AI Editor-in-Chief backend...")
    logger.info("Environment: %s", settings.app_env)

    # Initialize database tables
    await init_db()
    logger.info("Database initialized")

    # Start fetch scheduler
    start_fetch_scheduler()

    yield

    # ── Shutdown ─────────────────────────────────────────────────────
    logger.info("Shutting down...")
    stop_fetch_scheduler()
    await close_db()
    logger.info("Shutdown complete")


# ── Create App ───────────────────────────────────────────────────────

app = FastAPI(
    title="AI Editor-in-Chief",
    description=(
        "A lightweight RSS backend that fetches today's stories from configured "
        "sources and serves them to the frontend."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — allow all origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Register Routes ─────────────────────────────────────────────────

from app.api.routes.feeds import router as feeds_router
from app.api.routes.admin import router as admin_router

app.include_router(feeds_router)
app.include_router(admin_router)


# ── Health Check ────────────────────────────────────────────────────


@app.get("/health", response_model=HealthResponse, tags=["health"])
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="ok",
        version="1.0.0",
        environment=settings.app_env,
    )
