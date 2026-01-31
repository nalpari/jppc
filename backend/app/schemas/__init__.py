"""Pydantic schemas for API request/response validation."""

from app.schemas.company import (
    CompanyCreate,
    CompanyUpdate,
    CompanyResponse,
    CompanyListResponse,
)
from app.schemas.price import (
    PricePlanCreate,
    PricePlanUpdate,
    PricePlanResponse,
    PricePlanListResponse,
    PriceHistoryResponse,
    PriceCompareRequest,
    PriceCompareResponse,
    PriceCompareItem,
)
from app.schemas.crawling import (
    CrawlRequest,
    CrawlResponse,
    CrawlLogResponse,
    CrawlLogListResponse,
    CrawlStatusResponse,
    ScheduleConfig,
)
from app.schemas.alert import (
    AlertSettingCreate,
    AlertSettingUpdate,
    AlertSettingResponse,
    AlertRecipientCreate,
    AlertRecipientResponse,
)

__all__ = [
    # Company
    "CompanyCreate",
    "CompanyUpdate",
    "CompanyResponse",
    "CompanyListResponse",
    # Price
    "PricePlanCreate",
    "PricePlanUpdate",
    "PricePlanResponse",
    "PricePlanListResponse",
    "PriceHistoryResponse",
    "PriceCompareRequest",
    "PriceCompareResponse",
    "PriceCompareItem",
    # Crawling
    "CrawlRequest",
    "CrawlResponse",
    "CrawlLogResponse",
    "CrawlLogListResponse",
    "CrawlStatusResponse",
    "ScheduleConfig",
    # Alert
    "AlertSettingCreate",
    "AlertSettingUpdate",
    "AlertSettingResponse",
    "AlertRecipientCreate",
    "AlertRecipientResponse",
]
