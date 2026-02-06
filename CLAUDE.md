# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Japan Power Price Crawler (JPPC) - A full-stack application that automatically crawls and compares electricity price information from Japan's four major power companies (TEPCO, Chubu, Kepco, Chugoku). README and UI are in Korean.

## Commands

### Development Environment
```bash
docker compose up -d          # Start all services (frontend, backend, postgres)
docker compose logs -f        # View logs
docker compose down           # Stop services
```

### Backend (Python) — all commands run inside container
```bash
docker compose exec backend pytest                              # Run all tests
docker compose exec backend pytest tests/test_api/test_companies.py  # Single test file
docker compose exec backend pytest -k "test_create_company"     # Single test by name
docker compose exec backend pytest tests/test_e2e/              # E2E tests only
docker compose exec backend pytest --cov=app                    # With coverage
docker compose exec backend mypy app                            # Type checking
docker compose exec backend ruff check app                      # Linting
docker compose exec backend ruff check app --fix                # Lint autofix
docker compose exec backend black app                           # Formatting
```

### Frontend (Node.js) — run inside container or locally
```bash
docker compose exec frontend npm run dev          # Dev server
docker compose exec frontend npm run build        # Build
docker compose exec frontend npm run lint         # Lint
docker compose exec frontend npm run type-check   # TypeScript check
```

### Database Migrations (Alembic)
```bash
docker compose exec backend alembic upgrade head                          # Apply migrations
docker compose exec backend alembic revision --autogenerate -m "description"  # New migration
docker compose exec backend alembic downgrade -1                          # Rollback one
```

### Production
```bash
docker compose -f docker-compose.prod.yml --env-file .env.prod up -d --build
```

## Architecture

### Layered Backend (`backend/app/`)

```
API Layer (app/api/v1/)          → FastAPI routers, request validation
  ↓ uses DbSession = Annotated[AsyncSession, Depends(get_db)]
Service Layer (app/services/)    → Business logic (crawl_service, email_service, price_service)
  ↓
Model Layer (app/models/)        → SQLAlchemy 2.0 async ORM with Mapped[] types
  ↓
Database (PostgreSQL)            → Async via asyncpg, session auto-commit/rollback in get_db()
```

**Crawler subsystem** (`app/crawlers/`):
- `BaseCrawler` (ABC) with Template Method pattern — subclasses implement `_crawl_prices()` and `get_price_page_urls()`
- Concrete: `TEPCOCrawler`, `ChubuCrawler`, `KEPCOCrawler`, `ChugokuCrawler`
- `CRAWLER_REGISTRY` dict + `get_crawler(company_code)` factory in `__init__.py`
- Crawlers use Playwright (headless, ja-JP locale, Asia/Tokyo timezone, 30s timeout)
- `crawler_utils.py`: `RateLimiter`, `with_retry()` decorator, `parse_japanese_date()` (handles 令和/平成 eras)

**Data model relationships**:
```
Company (1) → (M) PricePlan (1) → (M) PriceHistory
Company (1) → (M) CrawlLog
```
- `PricePlan.price_tiers` and `PricePlan.time_of_use` are JSON columns for flexible pricing structures
- `PricePlan.raw_data` stores original crawled data
- `CrawlLog` tracks status: pending/running/success/failed/partial

**CrawlService** (`app/services/crawl_service.py`):
- Global singleton `crawl_service` manages async background crawl jobs
- `CrawlJob` tracks job_id, status, per-company results
- Flow: `start_crawl()` → `_execute_crawl()` → `_save_crawl_results()` → `_save_price_plan()` (with history tracking)

### Frontend (`frontend/src/`)

- **Next.js 14+** App Router, always dark mode, Korean locale (`lang="ko"`)
- **Path alias**: `@/*` → `./src/*`
- **Pages**: dashboard, companies, companies/[id], prices, prices/compare, prices/history, crawling, settings

**React Query pattern** (`src/hooks/`):
- Domain-specific hooks: `useCompanies`, `usePrices`, `useCrawling`, `useAlerts`, `useStats`
- Factory query keys: `companyKeys.all → .lists() → .list(params) → .details() → .detail(id)`
- Defaults: `staleTime: 60_000`, `refetchOnWindowFocus: false`, `retry: 1`
- Mutations invalidate related queries on success

**API client** (`src/lib/api.ts`):
- Centralized axios instance, base URL from `NEXT_PUBLIC_API_URL`
- Modular exports: `companiesApi`, `pricesApi`, `crawlingApi`, `alertsApi`, `statsApi`

**Components** (`src/components/`):
- `ui/` — Radix UI primitives: Button (CVA variants), Card (compound), Table, Modal, Select, Tabs, Loading/Skeleton
- `layout/` — MainLayout, Header, Sidebar (responsive with mobile drawer)
- Domain folders: `dashboard/`, `companies/`, `prices/`
- `providers/QueryProvider.tsx` wraps app with React Query defaults
- Utility `cn()` from `src/lib/utils.ts` merges Tailwind classes (clsx + tailwind-merge)

**Types** (`src/types/index.ts`):
- All TypeScript interfaces centralized: Company, PricePlan, PriceHistory, CrawlLog, AlertSetting
- Generic `PaginatedResponse<T>` for list endpoints

## Code Standards

### Backend
- Python 3.12+, strict type hints, `Mapped[]` for SQLAlchemy
- Black: line-length 100, target py312
- Ruff: rules E, F, I, N, W, UP (line-length 100)
- MyPy: strict mode, `ignore_missing_imports = true`
- pytest: `asyncio_mode = "auto"`, testpaths = `["tests"]`
- All DB operations async (`AsyncSession`, async context managers)

### Frontend
- TypeScript strict mode
- ESLint: `next/core-web-vitals`
- `'use client'` directive on all interactive pages
- Tailwind CSS with HSL CSS variable color system, class-based dark mode

## API

Base URL: `/api/v1/` — Swagger at `http://localhost:8080/docs`

| Route prefix | Purpose |
|-------------|---------|
| `/companies` | CRUD for power companies |
| `/prices` | Price plans, compare, history |
| `/crawling` | start, stop, status, logs, schedule |
| `/stats` | Dashboard aggregations |
| `/alerts` | Email notification settings |

## Testing

Tests in `backend/tests/`: `test_api/`, `test_crawlers/`, `test_e2e/`

Test fixtures (`conftest.py`): in-memory SQLite DB, `AsyncClient` with overridden `get_db`, sample data factories (`sample_company_data`, `sample_price_plan_data`).

## Ports

| Service | Dev Port |
|---------|----------|
| Frontend | 3001 |
| Backend API | 8080 (maps to 8000 inside container) |
| PostgreSQL | 5432 |

## Key Patterns

- **Dependency injection**: `DbSession` type alias in `app/api/deps.py` — use in all endpoint signatures
- **Adding a crawler**: subclass `BaseCrawler`, implement `_crawl_prices()` + `get_price_page_urls()`, register in `CRAWLER_REGISTRY`
- **Adding an endpoint**: create router in `app/api/v1/`, add schema in `app/schemas/`, include router in `app/api/v1/__init__.py`
- **Auth**: placeholder only (`get_current_user` returns hardcoded admin)
- **Scheduler**: APScheduler configured but not initialized (stubbed in `main.py`)
