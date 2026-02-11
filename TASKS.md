# Bookflix - Development Task Tracker

> **Status Legend**: [x] = Done | [ ] = Not done | [~] = Scaffold exists, needs testing/debugging

---

## Phase 0: First Boot (DO THIS FIRST)

These steps must happen before anything else works.

- [ ] Create `.env` from `.env.example` and fill in real values
- [ ] Run `npm install` in `frontend/` directory
- [ ] Run `docker compose up --build` and get all 8 services healthy
- [ ] Debug any startup errors (import errors, missing deps, config issues)
- [ ] Run `make migrate-create msg="initial"` to generate Alembic migration
- [ ] Run `make migrate` to apply migration to database
- [ ] Verify `init-db.sh` ran (pgvector + pg_trgm extensions created)
- [ ] Verify frontend loads at http://localhost:3000
- [ ] Verify backend API docs at http://localhost:8000/docs
- [ ] Verify Flower dashboard at http://localhost:5555

---

## Phase 1: Foundation & Infrastructure

### Infrastructure
- [x] `.gitignore` with comprehensive rules
- [x] `.env.example` with all config placeholders
- [x] `docker-compose.yml` - 8 services (db, redis, backend, worker-processing, worker-embedding, worker-llm, beat, frontend)
- [x] `backend/Dockerfile` - Python 3.12 with system deps
- [x] `frontend/Dockerfile` - Node 20 Alpine
- [x] `Makefile` - 12+ targets (up, down, build, logs, db-shell, migrate, etc.)
- [x] `scripts/init-db.sh` - pgvector + pg_trgm extension creation
- [x] `scripts/backup-db.sh` - pg_dump backup script

### Backend Foundation
- [x] `backend/pyproject.toml` - All dependencies declared
- [x] `backend/app/config.py` - Pydantic BaseSettings from env
- [x] `backend/app/main.py` - FastAPI app with CORS, lifespan, static files, health check
- [x] `backend/app/db/` - Async engine (asyncpg), sync engine (psycopg2), session factories, DeclarativeBase

### Database Models (all in `backend/app/models/`)
- [x] `book.py` - Book, BookFile (with tsvector search, GIN index)
- [x] `chunk.py` - BookChunk (with VECTOR(384), HNSW index)
- [x] `category.py` - Category (hierarchical), BookCategory, Tag, BookTag
- [x] `topic.py` - Topic (with VECTOR embedding), BookTopic, TopicRelation
- [x] `insight.py` - BookInsight (with VECTOR, HNSW), InsightConnection
- [x] `reading.py` - ReadingProgress, ReadingSession
- [x] `chat.py` - ChatSession, ChatMessage
- [x] `feed.py` - FeedItem
- [x] `processing.py` - ProcessingJob
- [x] `enrichment.py` - ExternalMetadata
- [x] `knowledge.py` - LearningPath, LearningPathBook
- [ ] Alembic initial migration generated and applied

### Celery Setup
- [x] `backend/celery_app/celery.py` - Celery instance with 3 queues (processing, embedding, llm)
- [x] `backend/celery_app/schedules.py` - Beat schedules (orchestrator, daily feed, weekly topics)
- [x] `backend/celery_app/tasks/book_tasks.py` - scan_library, extract_text, chunk_text, process_book
- [x] `backend/celery_app/tasks/embedding_tasks.py` - generate_book_embeddings
- [x] `backend/celery_app/tasks/insight_tasks.py` - generate_book_insights (multi-pass)
- [x] `backend/celery_app/tasks/enrichment_tasks.py` - enrich_book (Google Books API)
- [x] `backend/celery_app/tasks/topic_tasks.py` - rebuild_topics (KMeans)
- [x] `backend/celery_app/tasks/feed_tasks.py` - generate_daily_feed
- [x] `backend/celery_app/tasks/orchestrator_tasks.py` - orchestrator_tick

### Processing Pipeline
- [x] `backend/app/processing/extractors/pdf_extractor.py` - PyMuPDF text extraction
- [x] `backend/app/processing/extractors/epub_extractor.py` - ebooklib extraction
- [x] `backend/app/processing/chunker.py` - Recursive text chunking (512 tokens, 64 overlap)
- [x] `backend/app/processing/embedder.py` - SentenceTransformer batch embedding
- [x] `backend/app/processing/metadata_parser.py` - Title/author from file metadata
- [x] `backend/app/processing/pipeline.py` - DAG pipeline orchestrator

### LLM Layer
- [x] `backend/app/llm/client.py` - AsyncOpenAI wrapper for OpenRouter
- [x] `backend/app/llm/models.py` - ModelRegistry (per-task model routing)
- [x] `backend/app/llm/prompts.py` - All prompt templates

### Backend Services (all in `backend/app/services/`)
- [x] `book_service.py` - CRUD operations for books
- [x] `library_service.py` - Filesystem scanning, import, dedup
- [x] `search_service.py` - Hybrid search (FTS + vector + RRF fusion)
- [x] `insight_service.py` - Insight CRUD and generation triggers
- [x] `chat_service.py` - RAG chat pipeline (embed -> retrieve -> context -> LLM)
- [x] `feed_service.py` - Feed item CRUD and generation
- [x] `topic_service.py` - Topic modeling and graph
- [x] `recommendation_service.py` - Content-based recommendations
- [x] `reading_service.py` - Reading progress tracking
- [x] `knowledge_service.py` - Learning paths, connections
- [x] `enrichment_service.py` - External metadata fetching
- [x] `embedding_service.py` - Embedding generation management
- [x] `orchestrator_service.py` - Autonomous agent brain

### API Endpoints (all in `backend/app/api/v1/`)
- [x] `books.py` - 8 endpoints (CRUD, file serving, cover)
- [x] `library.py` - 5 endpoints (scan, import, stats, processing status)
- [x] `search.py` - 3 endpoints (hybrid search, suggest, passage search)
- [x] `insights.py` - 6 endpoints (by book, by id, concepts, frameworks, regenerate)
- [x] `chat.py` - 4 endpoints (sessions CRUD, send message)
- [x] `feed.py` - 4 endpoints (list, generate, update, daily digest)
- [x] `topics.py` - 3 endpoints (list, detail, graph)
- [x] `recommendations.py` - 2 endpoints (general, similar books)
- [x] `reading.py` - 5 endpoints (progress, update, sessions, stats)
- [x] `knowledge.py` - 4 endpoints (connections, learning paths, map)
- [x] `config.py` - 4 endpoints (get/update config, list models)
- [x] `ws.py` - WebSocket for processing progress + streaming chat
- [x] `router.py` - Master router mounting all sub-routers

### Pydantic Schemas (all in `backend/app/schemas/`)
- [x] `common.py` - Pagination, error responses
- [x] `book.py`, `search.py`, `insight.py`, `chat.py`
- [x] `feed.py`, `topic.py`, `reading.py`, `processing.py`

### Backend Utils
- [x] `file_utils.py` - File hashing, path validation
- [x] `text_utils.py` - Text cleaning, token counting
- [x] `image_utils.py` - Cover image processing
- [x] `ws_manager.py` - WebSocket connection manager

---

## Phase 1: Frontend

### Foundation
- [x] `package.json` - All dependencies declared
- [x] `vite.config.ts` - Dev server proxy to backend
- [x] `tsconfig.json` - TypeScript config
- [x] `tailwind.config.ts` - Dark Netflix theme
- [x] `index.css` - Global styles, dark theme
- [x] `main.tsx` - App entry with QueryClientProvider
- [x] `App.tsx` - React Router with 11 routes
- [ ] `npm install` run successfully
- [ ] Frontend builds without errors (`npm run build`)

### Core Libraries
- [x] `lib/api.ts` - All API functions (fetch wrapper)
- [x] `lib/ws.ts` - WebSocket client with auto-reconnect
- [x] `lib/utils.ts` - cn() utility

### Type Definitions
- [x] `types/book.ts`, `types/search.ts`, `types/chat.ts`
- [x] `types/insight.ts`, `types/feed.ts`, `types/api.ts`

### State Management
- [x] `stores/app-store.ts` - Zustand (sidebar, theme, search)
- [x] `stores/reading-store.ts` - Zustand (reading state)

### Hooks
- [x] `hooks/use-books.ts` - TanStack Query hooks for books
- [x] `hooks/use-search.ts` - Search with debounce
- [x] `hooks/use-chat.ts` - Chat session management
- [x] `hooks/use-reading.ts` - Reading progress
- [x] `hooks/use-websocket.ts` - WebSocket connection hook
- [x] `hooks/use-infinite-scroll.ts` - Infinite scroll pagination

### UI Components (shadcn/ui style)
- [x] button, card, input, badge, skeleton, progress
- [x] scroll-area, tabs, dialog, separator, tooltip

### Layout Components
- [x] `AppShell.tsx` - Main layout wrapper
- [x] `Sidebar.tsx` - Navigation sidebar
- [x] `TopBar.tsx` - Top bar with search
- [x] `MobileNav.tsx` - Mobile navigation

### Book Components
- [x] `BookCard.tsx` - Book card with cover
- [x] `BookGrid.tsx` - Responsive grid
- [x] `BookCover.tsx` - Cover image with fallback
- [x] `BookCarousel.tsx` - Horizontal scroll carousel

### Common Components
- [x] `LoadingState.tsx` - Loading spinner/skeleton
- [x] `EmptyState.tsx` - Empty state with icon
- [x] `ErrorBoundary.tsx` - Error boundary wrapper

### Pages (all scaffold with real UI code)
- [x] `HomePage.tsx` - Netflix-style carousels (continue reading, recent, by topic)
- [x] `BrowsePage.tsx` - Grid with filters and sorting
- [x] `BookPage.tsx` - Detail page with insights tabs
- [x] `ReaderPage.tsx` - PDF/EPUB reader (react-pdf / react-reader)
- [x] `SearchPage.tsx` - Search with filters and results
- [x] `ChatPage.tsx` - RAG chat interface with streaming
- [x] `FeedPage.tsx` - Social-style AI feed
- [x] `TopicsPage.tsx` - Topic cloud and knowledge graph
- [x] `KnowledgePage.tsx` - Second brain dashboard
- [x] `LibraryPage.tsx` - Library management (scan, import, progress)
- [x] `SettingsPage.tsx` - Configuration (models, paths, intensity)

---

## Phase 2: Testing & Debugging (NOT STARTED)

This is the critical next phase. All code exists but has never been run.

- [ ] Fix backend import errors (likely circular imports, missing __init__ exports)
- [ ] Fix frontend TypeScript errors (`npm run build` / `npx tsc --noEmit`)
- [ ] Fix frontend missing component imports (pages may reference components not yet created like search/, chat/, insights/, reader/ sub-components)
- [ ] Verify all Docker services start and stay healthy
- [ ] Verify database migration creates all tables correctly
- [ ] Test library scan endpoint with real book directory
- [ ] Test PDF text extraction with a real PDF
- [ ] Test EPUB text extraction with a real EPUB
- [ ] Test embedding generation
- [ ] Test search (full-text + semantic)
- [ ] Test chat RAG pipeline
- [ ] Test insight generation via LLM
- [ ] Test WebSocket connections (processing progress, chat streaming)
- [ ] Test frontend-backend API integration
- [ ] Test reading progress save/restore

### Known Likely Issues to Debug
- [ ] Frontend pages reference sub-components (search/, chat/, insights/, reader/) that don't exist yet as separate files - they may be inline or need to be created
- [ ] Some React imports may reference packages not in package.json (react-pdf, react-reader, react-force-graph, lucide-react)
- [ ] Backend circular imports between models/services/tasks
- [ ] Alembic may need manual tweaks for pgvector column types
- [ ] Celery task imports may have path issues depending on how the worker starts

---

## Phase 3: Feature Completion (NOT STARTED)

After debugging, these features may need additional work:

- [ ] PDF reader integration (react-pdf with virtualized pages)
- [ ] EPUB reader integration (react-reader / epub.js)
- [ ] Reader toolbar (font size, theme, TOC navigation)
- [ ] Search filters UI (search/, chat/, insights/ sub-components)
- [ ] Chat message streaming display
- [ ] Source citation cards in chat
- [ ] Knowledge graph visualization (react-force-graph)
- [ ] Topic cloud interactive component
- [ ] Feed card variations (TIL, connection, quote, suggestion)
- [ ] Learning path visualization
- [ ] Mobile responsive testing and fixes

---

## Phase 4: Polish & Production (NOT STARTED)

- [ ] Dark mode toggle (foundation exists in Tailwind config)
- [ ] Skeleton loading states on all pages
- [ ] Error boundaries on all route pages
- [ ] Toast notifications for actions
- [ ] Code splitting / lazy loading routes
- [ ] Virtualized lists for large book collections
- [ ] Image lazy loading
- [ ] Production Docker Compose (nginx, optimized builds)
- [ ] PWA manifest
- [ ] README.md with full documentation

---

## File Count Summary

| Directory | Files | Description |
|-----------|-------|-------------|
| Root | 6 | docker-compose, Makefile, .env.example, .gitignore, CLAUDE.md, TASKS.md |
| backend/app/models/ | 12 | SQLAlchemy ORM models |
| backend/app/schemas/ | 9 | Pydantic schemas |
| backend/app/api/ | 13 | API routes + WebSocket |
| backend/app/services/ | 13 | Business logic |
| backend/app/processing/ | 6 | Book processing pipeline |
| backend/app/llm/ | 3 | LLM abstraction |
| backend/app/utils/ | 4 | Utilities |
| backend/app/db/ | 3 | Database setup |
| backend/celery_app/ | 9 | Celery tasks |
| backend/ (other) | 5 | Dockerfile, pyproject.toml, alembic |
| frontend/src/pages/ | 11 | All pages |
| frontend/src/components/ | 22 | UI + layout + books + common |
| frontend/src/hooks/ | 6 | Custom hooks |
| frontend/src/stores/ | 2 | Zustand stores |
| frontend/src/lib/ | 3 | API, WebSocket, utils |
| frontend/src/types/ | 6 | TypeScript types |
| frontend/ (config) | 8 | Vite, TS, Tailwind, package.json |
| scripts/ | 2 | Shell scripts |
| **Total** | **~163** | |
