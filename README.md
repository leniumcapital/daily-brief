# Daily Brief

A personalized news curation agent that assembles a daily, dashboard-style briefing from X/Twitter and licensed news sources (RSS + aggregator APIs).

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│  X API      │     │  RSS Feeds   │     │  NewsAPI    │
│  (tweepy)   │     │ (feedparser) │     │  (httpx)    │
└──────┬──────┘     └──────┬───────┘     └──────┬──────┘
       │                   │                    │
       └───────────────────┼────────────────────┘
                           ▼
                  ┌─────────────────┐
                  │  Ingestion      │  APScheduler (separate cadences)
                  │  + Summarizer   │  Claude API (original summaries)
                  │  + Dedup        │  pgvector embeddings
                  └────────┬────────┘
                           ▼
                  ┌─────────────────┐
                  │  PostgreSQL     │  Articles, profiles, rankings
                  │  + Redis cache  │
                  └────────┬────────┘
                           ▼
                  ┌─────────────────┐
                  │  FastAPI        │  /api/v1/dashboard
                  └────────┬────────┘
                           ▼
                  ┌─────────────────┐
                  │  React Dashboard│  Vite + Tailwind + TanStack Query
                  └─────────────────┘
```

## Key design decisions

- **No paywall scraping** — RSS feeds and licensed APIs only
- **Category routing** — configurable source rankings per category (`backend/app/config/source_rankings.yaml`)
- **Deduplication** — embedding similarity clusters duplicate stories; highest-ranked source wins
- **Original summaries** — Claude generates paraphrased 2-3 sentence summaries
- **Serendipity slot** — ~10% of feed reserved for outside-interest stories
- **Graceful degradation** — stale content shown with clear labels when sources fail

## Connecting news outlets

All outlets are configured in `backend/app/config/sources.yaml`. Each source uses **legitimate access paths only** — official RSS feeds and licensed APIs. Providers are tried in order until one succeeds.

| Outlet | Primary API | Fallback |
|--------|-------------|----------|
| Bloomberg, WSJ, FT, CNBC | NewsAPI | RSS |
| TechCrunch, Ars Technica, Wired | NewsAPI | RSS |
| BBC (World & Business) | NewsAPI | RSS |
| The Guardian | Guardian Open Platform | RSS |
| NPR, Hacker News, AP | RSS | — |
| X / Twitter | Official X API v2 | — |

### 1. Add API keys to `.env`

```bash
cp .env.example .env
```

| Key | Where to get it | What it unlocks |
|-----|-----------------|-----------------|
| `NEWSAPI_KEY` | https://newsapi.org/register | Bloomberg, WSJ, FT, TechCrunch, BBC, etc. |
| `GUARDIAN_API_KEY` | https://open-platform.theguardian.com/access/ | The Guardian |
| `X_API_BEARER_TOKEN` | https://developer.x.com | X Tracker sidebar |
| `ANTHROPIC_API_KEY` | https://console.anthropic.com | AI summaries |

### 2. Test connections

```bash
curl -H "X-API-Key: dev-key" http://localhost:8000/api/v1/sources/status | python3 -m json.tool
```

Shows which outlets are connected and how many articles each returned.

### 3. Pull live articles

```bash
curl -X POST -H "X-API-Key: dev-key" http://localhost:8000/api/v1/refresh
```

The scheduler also auto-refreshes every 15 minutes.

## Quick start

### Prerequisites

- Docker & Docker Compose
- API keys: `NEWSAPI_KEY` (recommended), `GUARDIAN_API_KEY`, `X_API_BEARER_TOKEN`, `ANTHROPIC_API_KEY`

### Run (easiest)

```bash
cp .env.example .env
# Edit .env — set DATABASE_URL for your local Postgres user

./scripts/dev.sh
```

This starts both the API (port 8000) and dashboard (port 5173).

### Run manually

Dashboard: http://localhost:5173  
API docs: http://localhost:8000/docs

## Project structure

```
daily-brief/
├── backend/
│   ├── app/
│   │   ├── api/           # FastAPI routes
│   │   ├── config/        # Source rankings (YAML)
│   │   ├── models/        # SQLAlchemy models
│   │   ├── schemas/       # Pydantic response models
│   │   └── services/
│   │       ├── fetchers/  # RSS, Twitter, aggregator
│   │       ├── summarizer.py
│   │       ├── deduplication.py
│   │       ├── ranking.py
│   │       └── scheduler.py
│   └── pyproject.toml
├── frontend/              # React + Vite dashboard
└── docker-compose.yml
```

## License

Private — Lenium Capital
