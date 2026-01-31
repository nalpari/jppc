"""Statistics API endpoints."""

from datetime import datetime, timedelta

from fastapi import APIRouter
from sqlalchemy import select, func

from app.api.deps import DbSession
from app.models import Company, PricePlan, CrawlLog

router = APIRouter()


@router.get("/dashboard")
async def get_dashboard_stats(db: DbSession):
    """대시보드 통계 조회."""
    # Company stats
    total_companies = await db.scalar(select(func.count()).select_from(Company)) or 0
    active_companies = await db.scalar(
        select(func.count()).where(Company.is_active == True)
    ) or 0

    # Price plan stats
    total_plans = await db.scalar(select(func.count()).select_from(PricePlan)) or 0
    current_plans = await db.scalar(
        select(func.count()).where(PricePlan.is_current == True)
    ) or 0

    # Crawl stats
    total_crawls = await db.scalar(select(func.count()).select_from(CrawlLog)) or 0
    successful_crawls = await db.scalar(
        select(func.count()).where(CrawlLog.status == "success")
    ) or 0
    failed_crawls = await db.scalar(
        select(func.count()).where(CrawlLog.status == "failed")
    ) or 0

    # Last 7 days crawls
    week_ago = datetime.utcnow() - timedelta(days=7)
    recent_crawls = await db.scalar(
        select(func.count()).where(CrawlLog.started_at >= week_ago)
    ) or 0

    # Last successful crawl
    last_crawl_query = (
        select(CrawlLog)
        .where(CrawlLog.status == "success")
        .order_by(CrawlLog.finished_at.desc())
        .limit(1)
    )
    result = await db.execute(last_crawl_query)
    last_crawl = result.scalar_one_or_none()

    return {
        "companies": {
            "total": total_companies,
            "active": active_companies,
        },
        "price_plans": {
            "total": total_plans,
            "current": current_plans,
        },
        "crawling": {
            "total": total_crawls,
            "successful": successful_crawls,
            "failed": failed_crawls,
            "recent_7days": recent_crawls,
            "success_rate": (
                round(successful_crawls / total_crawls * 100, 1)
                if total_crawls > 0
                else 0
            ),
            "last_crawl_at": last_crawl.finished_at if last_crawl else None,
        },
    }


@router.get("/companies/{company_id}")
async def get_company_stats(db: DbSession, company_id: int):
    """전력회사별 통계 조회."""
    # Plans count
    total_plans = await db.scalar(
        select(func.count()).where(PricePlan.company_id == company_id)
    ) or 0
    current_plans = await db.scalar(
        select(func.count()).where(
            PricePlan.company_id == company_id,
            PricePlan.is_current == True,
        )
    ) or 0

    # Crawl stats
    total_crawls = await db.scalar(
        select(func.count()).where(CrawlLog.company_id == company_id)
    ) or 0
    successful_crawls = await db.scalar(
        select(func.count()).where(
            CrawlLog.company_id == company_id,
            CrawlLog.status == "success",
        )
    ) or 0

    # Last crawl
    last_crawl_query = (
        select(CrawlLog)
        .where(CrawlLog.company_id == company_id)
        .order_by(CrawlLog.started_at.desc())
        .limit(1)
    )
    result = await db.execute(last_crawl_query)
    last_crawl = result.scalar_one_or_none()

    return {
        "company_id": company_id,
        "price_plans": {
            "total": total_plans,
            "current": current_plans,
        },
        "crawling": {
            "total": total_crawls,
            "successful": successful_crawls,
            "success_rate": (
                round(successful_crawls / total_crawls * 100, 1)
                if total_crawls > 0
                else 0
            ),
            "last_crawl_at": last_crawl.started_at if last_crawl else None,
            "last_crawl_status": last_crawl.status if last_crawl else None,
        },
    }
