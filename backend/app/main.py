"""FastAPI application entry point."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import v1_router
from app.config import get_settings
from app.utils.logger import setup_logging, get_logger

settings = get_settings()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan handler."""
    # Startup
    setup_logging()
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")

    # TODO: Initialize scheduler if enabled
    # if settings.scheduler_enabled:
    #     from app.services.scheduler_service import start_scheduler
    #     start_scheduler()

    yield

    # Shutdown
    logger.info("Shutting down application")
    # TODO: Stop scheduler
    # if settings.scheduler_enabled:
    #     from app.services.scheduler_service import stop_scheduler
    #     stop_scheduler()


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="일본 주요 전력회사 요금 정보 자동 수집 시스템",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(v1_router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": settings.app_version,
    }
