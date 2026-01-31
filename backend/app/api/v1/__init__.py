"""API v1 routes."""

from fastapi import APIRouter

from app.api.v1 import companies, prices, crawling, alerts, stats

router = APIRouter(prefix="/api/v1")

router.include_router(companies.router, prefix="/companies", tags=["Companies"])
router.include_router(prices.router, prefix="/prices", tags=["Prices"])
router.include_router(crawling.router, prefix="/crawling", tags=["Crawling"])
router.include_router(alerts.router, prefix="/alerts", tags=["Alerts"])
router.include_router(stats.router, prefix="/stats", tags=["Statistics"])
