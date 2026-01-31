"""Services package for business logic."""

from app.services.crawl_service import CrawlService, CrawlJob, CrawlStatus, crawl_service
from app.services.scheduler_service import SchedulerService, scheduler_service
from app.services.email_service import EmailService, EmailMessage, email_service
from app.services.data_validation import (
    PriceDataValidator,
    PriceChangeDetector,
    ValidationResult,
    PriceChange,
)
from app.services.price_service import PriceService, price_service

__all__ = [
    # Crawl service
    "CrawlService",
    "CrawlJob",
    "CrawlStatus",
    "crawl_service",
    # Scheduler service
    "SchedulerService",
    "scheduler_service",
    # Email service
    "EmailService",
    "EmailMessage",
    "email_service",
    # Data validation
    "PriceDataValidator",
    "PriceChangeDetector",
    "ValidationResult",
    "PriceChange",
    # Price service
    "PriceService",
    "price_service",
]
