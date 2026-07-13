# Project Overview

`newspaper-ai` is now an RSS-first news reader. The app fetches stories from a fixed set of RSS feeds, keeps only today’s items, deduplicates them, stores them in Postgres, and serves them to a TanStack Start frontend with a swipe-card reading experience.

## Current Architecture

- Backend: FastAPI + PostgreSQL.
- Fetching: RSS-only, no LLM pipeline in the active flow.
- Frontend: TanStack Start app in `frontend/`, built for Vercel.
- Data model: `Source` and `RawStory` are the only active database entities.

## What The App Does

1. Loads RSS sources from `app/fetchers/sources.yaml`.
2. Fetches stories from those feeds.
3. Keeps only stories published today in `Asia/Kolkata`.
4. Deduplicates by URL and title/source timing.
5. Stores raw stories in Postgres.
6. Groups stories by section for the frontend.
7. Renders a left/right swipe deck on the home page.

## Backend Status

- `app/main.py` starts the FastAPI app and the fetch scheduler.
- `GET /health` returns app status.
- `POST /admin/run-fetch` manually triggers one fetch cycle.
- `GET /admin/stats` shows raw story and source counts.
- `GET /feeds/sections` returns the grouped RSS sections for the frontend.

## Frontend Status

- The Lovable-based frontend now lives in `frontend/`.
- The home page uses the original swipe-card layout.
- Section tabs sit below the nav bar and switch the swipe deck content.
- Story images are extracted from RSS enclosures and displayed in cards.
- Production builds are configured for Vercel through Nitro.

## Removed / No Longer Active

- The old clustering, rewriting, ranking, and edition-generation pipeline.
- Alembic-related code paths.
- The old article detail and editions API flow.
- Groq-based LLM calls in the main user flow.

## Main Files

- Backend entrypoint: [app/main.py](/Users/yashpawar/newspaper-ai/app/main.py)
- Backend config: [app/config.py](/Users/yashpawar/newspaper-ai/app/config.py)
- Database models: [app/db/models.py](/Users/yashpawar/newspaper-ai/app/db/models.py)
- RSS fetch manager: [app/fetchers/manager.py](/Users/yashpawar/newspaper-ai/app/fetchers/manager.py)
- RSS section API: [app/api/routes/feeds.py](/Users/yashpawar/newspaper-ai/app/api/routes/feeds.py)
- Admin routes: [app/api/routes/admin.py](/Users/yashpawar/newspaper-ai/app/api/routes/admin.py)
- Frontend Vercel config: [frontend/vite.config.ts](/Users/yashpawar/newspaper-ai/frontend/vite.config.ts)
- Frontend home page: [frontend/src/routes/index.tsx](/Users/yashpawar/newspaper-ai/frontend/src/routes/index.tsx)
- Frontend RSS data layer: [frontend/src/lib/news.server.ts](/Users/yashpawar/newspaper-ai/frontend/src/lib/news.server.ts)

## Local Run

Backend:

```bash
cd /Users/yashpawar/newspaper-ai
source .venv/bin/activate
uvicorn app.main:app --reload
```

Frontend:

```bash
cd /Users/yashpawar/newspaper-ai/frontend
npm install
npm run dev
```

## Deployment Shape

- Deploy the frontend to Vercel.
- Deploy the FastAPI backend on Railway.
- Set `BACKEND_API_BASE` in Vercel to the Railway backend URL.
- Set the Railway environment variables for database connection, admin token, and CORS origins.

## Current Verification

- Backend Python files compile successfully.
- Frontend production build succeeds with the Vercel preset.
- API and fetcher tests pass locally.
