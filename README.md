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

## Quick start

### Prerequisites

- Docker & Docker Compose
- API keys: `ANTHROPIC_API_KEY`, `X_API_BEARER_TOKEN` (paid tier), `NEWSAPI_KEY` (optional)

### Run

```bash
cp .env.example .env
# Edit .env with your API keys

docker compose up -d postgres redis
cd backend && pip install -e . && uvicorn app.main:app --reload

cd frontend && npm install && npm run dev
```

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
