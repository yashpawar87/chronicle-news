# Live RSS, No Database

## Summary
Convert the backend into a thin live-RSS API that fetches and parses the configured feeds on each request, with no Postgres, scheduler, persistence layer, or admin fetch flow. The frontend keeps the current swipe deck and section tabs, but it reads from live backend responses instead of database-backed stories.

## Key Changes
- Replace the DB-backed feed path with an on-demand RSS aggregation path in the backend.
- Remove startup-time database initialization, session setup, models, and scheduler wiring so the app boots without any persistence dependency.
- Keep `GET /feeds/sections` as the main API, but have it call the RSS fetchers directly and return sectioned stories in the same shape the frontend already expects.
- Drop or retire admin-only DB endpoints like `POST /admin/run-fetch` and `GET /admin/stats`, since there is no stored data to manage.
- Simplify deployment env vars to only the live-runtime values: `APP_ENV`, `CORS_ALLOWED_ORIGINS`, `BACKEND_API_BASE`, and any fetch/caching knobs we decide to keep.
- Update the project overview and deployment notes so they describe a live RSS backend rather than a database-backed pipeline.

## Test Plan
- Verify the app boots cleanly with no `DATABASE_URL` set.
- Verify `GET /health` returns `ok` without touching any DB code.
- Verify `GET /feeds/sections` returns live section data from the YAML sources and still includes image URLs.
- Verify the frontend still renders the swipe deck and section tabs against the live backend contract.
- Smoke test a deploy on the target platform with the DB-related env vars removed.

## Assumptions
- We keep the current frontend experience and API response shape intact.
- We keep the source list in `app/fetchers/sources.yaml` as the single configuration source.
- Stories are fetched per request, not cached in Postgres or written anywhere durable.
- The existing `max 8 stories per section` behavior stays unless you want to change it later.
