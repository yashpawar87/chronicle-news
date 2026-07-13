"""FastAPI application entrypoint for the RSS backend.

Registers all routes and starts the application.
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
    # ── Startup ──────────────────────────────────────────────────────
    logger.info("Starting AI Editor-in-Chief backend...")
    logger.info("Environment: %s", settings.app_env)

    yield

    # ── Shutdown ─────────────────────────────────────────────────────
    logger.info("Shutting down...")
    logger.info("Shutdown complete")


# ── Create App ───────────────────────────────────────────────────────

app = FastAPI(
    title="AI Editor-in-Chief",
    description=(
        "A lightweight RSS backend that fetches today's stories from configured "
        "sources and serves them to the frontend live."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Register Routes ─────────────────────────────────────────────────

from app.api.routes.feeds import router as feeds_router

app.include_router(feeds_router)


# ── Health Check ────────────────────────────────────────────────────


@app.get("/health", response_model=HealthResponse, tags=["health"])
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="ok",
        version="1.0.0",
        environment=settings.app_env,
    )
