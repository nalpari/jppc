# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Japan Power Price Crawler (JPPC) - A full-stack application that automatically crawls and compares electricity price information from Japan's four major power companies (TEPCO, Chubu, Kepco, Chugoku).

## Commands

### Development Environment
```bash
# Start all services (frontend, backend, postgres)
docker compose up -d

# View logs
docker compose logs -f

# Stop services
docker compose down
```

### Backend (Python)
```bash
# Run tests
docker compose exec backend pytest

# Run tests with coverage
docker compose exec backend pytest --cov=app

# Run E2E tests only
docker compose exec backend pytest tests/test_e2e/

# Type checking
docker compose exec backend mypy app

# Linting
docker compose exec backend ruff check app

# Formatting
docker compose exec backend black app
```

### Frontend (Node.js)
```bash
# Development server (inside container or locally)
npm run dev

# Build
npm run build

# Lint
npm run lint

# Type check
npm run type-check
```

### Production Deployment
```bash
docker compose -f docker-compose.prod.yml --env-file .env.prod up -d --build
```

### Database Migrations (Alembic)
```bash
docker compose exec backend alembic upgrade head
docker compose exec backend alembic revision --autogenerate -m "description"
```

## Architecture

### Backend (`backend/`)
- **FastAPI** async REST API with Pydantic v2 schemas
- **SQLAlchemy 2.0** async ORM with PostgreSQL
- **Playwright** for browser-based web crawling

Key directories:
- `app/api/v1/` - REST endpoints (companies, prices, crawling, alerts, stats)
- `app/crawlers/` - Per-company crawler implementations inheriting from `base_crawler.py`
- `app/services/` - Business logic layer (crawl_service, email_service)
- `app/models/` - SQLAlchemy models using `Mapped[]` type hints
- `app/schemas/` - Pydantic request/response schemas

### Frontend (`frontend/`)
- **Next.js 14+** with App Router (`src/app/`)
- **React Query** for server state management
- **Radix UI + TailwindCSS** component library

Key directories:
- `src/app/` - Page routes (dashboard, companies, prices, settings, crawling)
- `src/components/` - Domain-organized React components
- `src/hooks/` - React Query custom hooks
- `src/lib/api.ts` - Centralized axios client

### Data Flow
1. Crawlers fetch data from power company websites using Playwright
2. Data is validated, normalized, and stored in PostgreSQL
3. REST API exposes data to frontend
4. React Query handles caching and refetching

## Code Standards

### Backend
- Python 3.12+ with strict type hints
- Black: 100 char line length
- Ruff: E, F, I, N, W, UP rules
- MyPy: strict mode
- All database operations must be async

### Frontend
- TypeScript strict mode
- ESLint with `next/core-web-vitals`
- Use `'use client'` directive for interactive components

## API Base URL

All API endpoints are under `/api/v1/`:
- `/companies` - Power company management
- `/prices` - Price plans and comparison
- `/crawling/start`, `/crawling/status`, `/crawling/logs` - Crawler control
- `/stats/dashboard` - Dashboard aggregations
- `/alerts` - Email notification settings

## Environment Variables

Key variables (see `.env.example` for full list):
- `DATABASE_URL` - PostgreSQL connection string
- `NEXT_PUBLIC_API_URL` - Backend URL for frontend
- `SMTP_*` - Email notification configuration

## Ports

| Service | Dev Port |
|---------|----------|
| Frontend | 3001 |
| Backend API | 8080 |
| PostgreSQL | 5432 |
