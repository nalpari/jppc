"""Crawling schemas for API validation."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class CrawlRequest(BaseModel):
    """Schema for crawl request."""

    company_ids: list[int] | None = Field(
        None, description="크롤링할 전력회사 ID 목록 (None이면 전체)"
    )
    force: bool = Field(default=False, description="강제 크롤링 여부")


class CrawlResponse(BaseModel):
    """Schema for crawl response."""

    crawl_id: int
    status: str
    message: str
    companies: list[str] = Field(default_factory=list, description="대상 전력회사 목록")


class CrawlLogResponse(BaseModel):
    """Schema for crawl log response."""

    id: int
    company_id: int | None
    company_name: str | None = None
    status: str
    trigger_type: str
    started_at: datetime
    finished_at: datetime | None
    duration_seconds: int | None
    plans_found: int
    plans_updated: int
    plans_created: int
    error_message: str | None
    error_details: dict[str, Any] | None

    model_config = {"from_attributes": True}


class CrawlLogListResponse(BaseModel):
    """Schema for crawl log list response."""

    items: list[CrawlLogResponse]
    total: int
    page: int = 1
    page_size: int = 20


class CrawlStatusResponse(BaseModel):
    """Schema for current crawl status."""

    is_running: bool
    current_crawl_id: int | None = None
    current_company: str | None = None
    progress: int = Field(default=0, ge=0, le=100, description="진행률 (%)")
    last_crawl_at: datetime | None = None
    next_scheduled_at: datetime | None = None


class ScheduleConfig(BaseModel):
    """Schema for schedule configuration."""

    enabled: bool = Field(default=True, description="스케줄 활성화 여부")
    day_of_week: int = Field(
        default=1, ge=0, le=6, description="요일 (0=일, 1=월, ..., 6=토)"
    )
    hour: int = Field(default=2, ge=0, le=23, description="시간 (0-23)")
    minute: int = Field(default=0, ge=0, le=59, description="분 (0-59)")
    timezone: str = Field(default="Asia/Tokyo", description="타임존")
