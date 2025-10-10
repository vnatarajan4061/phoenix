# Phoenix

MLB data ingestion pipeline for Beat the Streak predictions and real-time game analytics.

## Overview

Hybrid batch + real-time pipeline that ingests MLB data into PostgreSQL/Supabase for ML analysis and app consumption.

## Architecture

### Phase 1: Batch Ingestion (Current)
Daily jobs for historical/scheduled data:
- Team schedules (next 30 days)
- Player season stats
- Completed game results
- Runs at 3 AM via cron

### Phase 2: Live Polling (Future)
Real-time ingestion during games:
- At-bat updates every 15 seconds
- Live scores and inning data
- Only polls active games (12 PM - 11 PM)

### Phase 3: ML & Apps (Future)
- Beat the Streak ML models
- Player performance predictions
- Mobile/web apps with real-time updates

See [DATA_INGESTION_ARCHITECTURE.md](DATA_INGESTION_ARCHITECTURE.md) for complete documentation.

## Tech Stack

- Python 3.13+ with async/await
- SQLAlchemy + asyncpg (database ORM)
- Pydantic (API validation)
- Supabase/PostgreSQL (storage + real-time push)
- Alembic (migrations)

## Quick Start

1. **Install dependencies**
   ```bash
   uv sync
   ```

2. **Configure environment**
   ```bash
   # Create .env
   MLB_API=https://statsapi.mlb.com/api
   DATABASE_URL=postgresql+asyncpg://postgres:password@db.project.supabase.co:5432/postgres
   ```

3. **Create database tables**
   ```bash
   alembic upgrade head
   ```

4. **Run batch ingestion**
   ```bash
   python -m src.ingest-mlb.main
   ```

## Project Structure

```
src/
├── common/          # Shared utilities and base models
├── ingest-mlb/      # MLB API client & Pydantic models
└── database/        # SQLAlchemy models & ingestion logic
```

## Development

```bash
# Format & lint
black src/ && ruff check --fix src/

# Run tests
pytest

# Add dependencies
uv add package-name
```

## Data Flow

```
MLB Stats API → Pydantic Validation → SQLAlchemy → Supabase PostgreSQL → Real-Time Push → Apps
```

---

**Status**: Phase 1 - In Progress
**Documentation**: [Architecture Guide](DATA_INGESTION_ARCHITECTURE.md)
