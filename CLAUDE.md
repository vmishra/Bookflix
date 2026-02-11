# Bookflix - Project Guide for Claude

## What This Project Is

Bookflix is a Netflix-style web app for a personal book library (thousands of PDFs/EPUBs on an external disk mounted on a Linux Mint PC). It provides AI-powered insights, semantic search, chat with books, topic modeling, a social-style feed, and a "second brain" knowledge system.

The backend runs on the Linux machine and is accessible from any device on the local network.

## Tech Stack

- **Frontend**: React 18 + Vite 6 + TypeScript + TailwindCSS + shadcn/ui
- **Backend**: Python 3.12 + FastAPI + SQLAlchemy (async) + Alembic
- **Database**: PostgreSQL 16 + pgvector (single DB for relational + vector)
- **Task Queue**: Celery + Redis (broker + cache + pub/sub)
- **LLM**: OpenRouter API (default: `stepfun/step-3.5-flash:free`)
- **Embeddings**: sentence-transformers (local `all-MiniLM-L6-v2`, 384-dim)
- **PDF**: PyMuPDF (fitz) + pdfplumber | **EPUB**: ebooklib
- **Deployment**: Docker Compose (8 services)
- **Reader**: react-pdf (PDF) + react-reader/epub.js (EPUB)

## Project Structure

```
bookflix/
├── CLAUDE.md              # This file
├── TASKS.md               # Detailed task tracker (what's done, what's not)
├── .env.example           # Template - copy to .env and fill in
├── .gitignore             # Comprehensive - .env is gitignored
├── docker-compose.yml     # 8 services: db, redis, backend, 3 workers, beat, frontend
├── Makefile               # make up, make down, make logs, make migrate, etc.
├── scripts/
│   ├── init-db.sh         # Creates pgvector + pg_trgm extensions
│   └── backup-db.sh       # pg_dump backup
├── backend/
│   ├── Dockerfile
│   ├── pyproject.toml     # All Python dependencies
│   ├── alembic.ini + alembic/
│   └── app/
│       ├── main.py        # FastAPI app entry point
│       ├── config.py      # Pydantic BaseSettings
│       ├── db/            # engine.py, session.py, base.py
│       ├── models/        # 12 SQLAlchemy models (book, chunk, insight, chat, feed, etc.)
│       ├── schemas/       # 9 Pydantic request/response modules
│       ├── api/           # router.py + v1/ (11 route files) + ws.py
│       ├── services/      # 12 business logic modules
│       ├── processing/    # PDF/EPUB extractors, chunker, embedder, pipeline
│       ├── llm/           # client.py, models.py, prompts.py
│       └── utils/         # file, text, image utils + WebSocket manager
│   └── celery_app/
│       ├── celery.py      # Celery instance
│       ├── schedules.py   # Beat schedules
│       └── tasks/         # 7 task modules + orchestrator
└── frontend/
    ├── Dockerfile
    ├── package.json
    ├── vite.config.ts, tailwind.config.ts, tsconfig.json
    └── src/
        ├── pages/         # 11 pages (Home, Browse, Book, Reader, Search, Chat, Feed, Topics, Knowledge, Library, Settings)
        ├── components/    # ui/ (11 shadcn), layout/ (4), books/ (4), common/ (3)
        ├── hooks/         # 6 custom hooks (books, search, chat, reading, websocket, infinite-scroll)
        ├── stores/        # Zustand stores (app-store, reading-store)
        ├── lib/           # api.ts, ws.ts, utils.ts
        └── types/         # 6 type definition files
```

## Current State (as of initial scaffold)

**ALL CODE IS SCAFFOLD** - the full structure is in place with real logic in all files, but nothing has been tested end-to-end yet. See `TASKS.md` for the exact status of every component.

### What IS done (Phase 1 scaffold):
- All 160 files created with actual implementation code
- Docker Compose with all 8 services configured
- All SQLAlchemy models with pgvector columns and indexes
- All Celery tasks with real processing logic
- All API endpoints wired up
- All frontend pages with UI components
- All services with business logic

### What is NOT done yet:
- `npm install` has never been run (no node_modules)
- No Alembic migration generated yet
- No `.env` file created (only `.env.example`)
- Nothing has been tested - no `docker compose up` yet
- Frontend may have import errors or missing dependencies
- Backend may have import errors or circular dependencies
- No actual data has been processed

## How to Get Running

```bash
# 1. Copy and fill in environment variables
cp .env.example .env
# Edit .env with real values (OPENROUTER_API_KEY, BOOKS_PATH, etc.)

# 2. Start all services
docker compose up --build

# 3. Generate and run migrations (after backend is up)
make migrate-create msg="initial"
make migrate

# 4. Access the app
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000/docs
# Flower (Celery monitor): http://localhost:5555
```

## Key Configuration (.env)

The most important env vars to set:
- `OPENROUTER_API_KEY` - Get from openrouter.ai
- `BOOKS_PATH` - Absolute path to the mounted external disk with PDFs/EPUBs
- `DATABASE_URL` - Default works with docker-compose
- `REDIS_URL` - Default works with docker-compose

## Development Phases

The project follows 6 phases. See `TASKS.md` for detailed checklist.

1. **Foundation & Infrastructure** - Scaffold done, needs testing/debugging
2. **Search & Reading** - Scaffold done, needs testing/debugging
3. **AI Insights & Chat** - Scaffold done, needs testing/debugging
4. **Topics, Feed & Knowledge Graph** - Scaffold done, needs testing/debugging
5. **Recommendations & Autonomous Agent** - Scaffold done, needs testing/debugging
6. **Polish & Production** - Not started

## Important Notes

- **No secrets in git**: `.env` is gitignored. Only `.env.example` with placeholders is committed.
- **The OpenRouter API key** goes ONLY in `.env`.
- **Book files are read-only**: The app never modifies files on the external disk.
- **User preference**: Do NOT include `Co-Authored-By: Claude` in commit messages.
