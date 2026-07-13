# Project Overview

`newspaper-ai` is now a stateless, live RSS-first news reader API. The app fetches stories from a fixed set of RSS feeds on-demand without storing anything in a database, and serves them to a TanStack Start frontend with a swipe-card reading experience.

## Current Architecture

- Backend: FastAPI (Stateless, live RSS fetcher API)
- Fetching: Concurrent live RSS parsing on every request.
- Frontend: TanStack Start app in `frontend/`, built for Vercel.
- Data model: No persistence.

## What The App Does

1. Loads RSS sources from `app/fetchers/sources.yaml`.
2. When the frontend requests `/feeds/sections`, it fetches the latest stories directly from the RSS feeds.
3. Groups stories by section for the frontend.
4. Renders a left/right swipe deck on the home page.

## Backend Status

- `app/main.py` starts the FastAPI app.
- `GET /health` returns app status.
- `GET /feeds/sections` returns the grouped live RSS sections for the frontend.
- **Removed**: Postgres, SQLAlchemy, Background Scheduler, Admin endpoints.

## Frontend Status

- The Lovable-based frontend lives in `frontend/`.
- The home page uses the original swipe-card layout.
- Section tabs sit below the nav bar and switch the swipe deck content.
- Story images are extracted from RSS enclosures and displayed in cards.
- Production builds are configured for Vercel through Nitro.

## Main Files

- Backend entrypoint: [app/main.py](/Users/yashpawar/newspaper-ai/app/main.py)
- Backend config: [app/config.py](/Users/yashpawar/newspaper-ai/app/config.py)
- RSS fetcher: [app/fetchers/rss/rss_fetcher.py](/Users/yashpawar/newspaper-ai/app/fetchers/rss/rss_fetcher.py)
- RSS section API: [app/api/routes/feeds.py](/Users/yashpawar/newspaper-ai/app/api/routes/feeds.py)
- Frontend Vercel config: [frontend/vite.config.ts](/Users/yashpawar/newspaper-ai/frontend/vite.config.ts)

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

## Deployment Shape (100% Vercel)

You can now deploy both the frontend and backend to Vercel for free!

**1. Deploy the Backend (Python API):**
- Create a New Project in Vercel.
- Import the `yashpawar87/chronicle-news` repository.
- Leave the Root Directory as `/`.
- Vercel will automatically detect `vercel.json` and deploy your FastAPI backend as a Serverless Function.
- Copy the backend URL (e.g., `https://chronicle-news-backend.vercel.app`).

**2. Deploy the Frontend:**
- Create another New Project in Vercel.
- Import the `yashpawar87/chronicle-news` repository again.
- **CRITICAL:** Set the **Root Directory** to `frontend`.
- Add an Environment Variable: `BACKEND_API_BASE` set to the backend URL you copied in step 1.
- Deploy!

**3. Set CORS:**
- Go back to your Backend project in Vercel -> Settings -> Environment Variables.
- Add `CORS_ALLOWED_ORIGINS` and set it to your frontend URL.
- Redeploy the backend.
