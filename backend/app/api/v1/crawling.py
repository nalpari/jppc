"""Crawling API endpoints."""

from datetime import datetime

from fastapi import APIRouter, HTTPException, Query, BackgroundTasks
from sqlalchemy import select, func

from app.api.deps import DbSession
from app.db.database import async_session_maker
from app.models import Company, CrawlLog
from app.schemas import (
    CrawlRequest,
    CrawlResponse,
    CrawlLogResponse,
    CrawlLogListResponse,
    CrawlStatusResponse,
    ScheduleConfig,
)
from app.services.crawl_service import crawl_service
from app.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()

# In-memory state for current crawl status
_crawl_state = {
    "is_running": False,
    "current_crawl_id": None,
    "current_company": None,
    "progress": 0,
}


async def run_crawl_task(crawl_log_id: int, company_codes: list[str]) -> None:
    """Background task to run crawling.

    Args:
        crawl_log_id: ID of the crawl log to update
        company_codes: List of company codes to crawl
    """
    global _crawl_state

    _crawl_state["is_running"] = True
    _crawl_state["current_crawl_id"] = crawl_log_id
    _crawl_state["progress"] = 0

    try:
        async with async_session_maker() as db:
            # Update crawl log status to running
            crawl_log = await db.scalar(
                select(CrawlLog).where(CrawlLog.id == crawl_log_id)
            )
            if crawl_log:
                crawl_log.status = "running"
                crawl_log.started_at = datetime.utcnow()
                await db.commit()

            # Start crawling using the service
            total_companies = len(company_codes) if company_codes else 4  # Default 4 companies
            plans_found = 0
            plans_created = 0
            plans_updated = 0

            job = await crawl_service.start_crawl(
                db,
                company_codes=company_codes if company_codes else None,
                headless=True,
            )

            # Wait for job to complete (poll status)
            import asyncio
            while job.status.value in ("pending", "running"):
                await asyncio.sleep(1)
                # Update progress based on completed results
                completed = len(job.results)
                if total_companies > 0:
                    _crawl_state["progress"] = int((completed / total_companies) * 100)

                # Update current company being crawled
                for code in (company_codes or []):
                    if code not in job.results:
                        _crawl_state["current_company"] = code
                        break

            # Calculate totals from results
            for code, result in job.results.items():
                if result.success:
                    plans_found += len(result.plans)

            # Update crawl log with final status
            crawl_log = await db.scalar(
                select(CrawlLog).where(CrawlLog.id == crawl_log_id)
            )
            if crawl_log:
                if job.status.value == "success":
                    crawl_log.mark_success(plans_found, plans_updated, plans_created)
                elif job.status.value == "partial":
                    crawl_log.status = "partial"
                    crawl_log.finished_at = datetime.utcnow()
                    crawl_log.duration_seconds = int(
                        (crawl_log.finished_at - crawl_log.started_at).total_seconds()
                    )
                    crawl_log.plans_found = plans_found
                else:
                    crawl_log.mark_failed(job.error or "Crawl failed")

                await db.commit()

            logger.info(f"Crawl job {crawl_log_id} completed with status: {job.status.value}")

    except Exception as e:
        logger.error(f"Crawl task failed: {e}")
        # Update crawl log with error
        try:
            async with async_session_maker() as db:
                crawl_log = await db.scalar(
                    select(CrawlLog).where(CrawlLog.id == crawl_log_id)
                )
                if crawl_log:
                    crawl_log.mark_failed(str(e))
                    await db.commit()
        except Exception as db_error:
            logger.error(f"Failed to update crawl log: {db_error}")

    finally:
        _crawl_state["is_running"] = False
        _crawl_state["current_crawl_id"] = None
        _crawl_state["current_company"] = None
        _crawl_state["progress"] = 0


@router.post("/start", response_model=CrawlResponse)
async def start_crawl(
    db: DbSession,
    data: CrawlRequest,
    background_tasks: BackgroundTasks,
):
    """크롤링 시작."""
    if _crawl_state["is_running"]:
        raise HTTPException(status_code=409, detail="Crawl already in progress")

    # Get target companies
    if data.company_ids:
        query = select(Company).where(
            Company.id.in_(data.company_ids),
            Company.is_active == True,
        )
    else:
        query = select(Company).where(Company.is_active == True)

    result = await db.execute(query)
    companies = result.scalars().all()

    if not companies:
        raise HTTPException(status_code=404, detail="No active companies found")

    # Create crawl log
    crawl_log = CrawlLog(
        status="pending",
        trigger_type="manual",
    )
    db.add(crawl_log)
    await db.flush()
    await db.refresh(crawl_log)

    company_names = [c.name_en for c in companies]
    company_codes = [c.code for c in companies]

    # Start actual crawling in background
    background_tasks.add_task(run_crawl_task, crawl_log.id, company_codes)

    return CrawlResponse(
        crawl_id=crawl_log.id,
        status="pending",
        message=f"Crawl started for {len(companies)} companies",
        companies=company_names,
    )


@router.post("/stop")
async def stop_crawl(db: DbSession):
    """크롤링 중지."""
    if not _crawl_state["is_running"]:
        raise HTTPException(status_code=400, detail="No crawl in progress")

    # Cancel active jobs in CrawlService
    active_jobs = crawl_service.get_active_jobs()
    for job in active_jobs:
        await crawl_service.cancel_job(job.job_id)

    # Update crawl log if exists
    crawl_log_id = _crawl_state["current_crawl_id"]
    if crawl_log_id:
        crawl_log = await db.scalar(
            select(CrawlLog).where(CrawlLog.id == crawl_log_id)
        )
        if crawl_log and crawl_log.status in ("pending", "running"):
            crawl_log.status = "cancelled"
            crawl_log.finished_at = datetime.utcnow()
            if crawl_log.started_at:
                crawl_log.duration_seconds = int(
                    (crawl_log.finished_at - crawl_log.started_at).total_seconds()
                )

    _crawl_state["is_running"] = False
    _crawl_state["current_crawl_id"] = None
    _crawl_state["current_company"] = None
    _crawl_state["progress"] = 0

    return {"message": "Crawl stopped"}


@router.get("/status", response_model=CrawlStatusResponse)
async def get_crawl_status(db: DbSession):
    """현재 크롤링 상태 조회."""
    # Get last crawl
    last_crawl_query = (
        select(CrawlLog)
        .where(CrawlLog.status == "success")
        .order_by(CrawlLog.finished_at.desc())
        .limit(1)
    )
    result = await db.execute(last_crawl_query)
    last_crawl = result.scalar_one_or_none()

    return CrawlStatusResponse(
        is_running=_crawl_state["is_running"],
        current_crawl_id=_crawl_state["current_crawl_id"],
        current_company=_crawl_state["current_company"],
        progress=_crawl_state["progress"],
        last_crawl_at=last_crawl.finished_at if last_crawl else None,
        next_scheduled_at=None,  # TODO: Get from scheduler
    )


@router.get("/logs", response_model=CrawlLogListResponse)
async def list_crawl_logs(
    db: DbSession,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    company_id: int | None = None,
    status: str | None = None,
):
    """크롤링 이력 조회."""
    query = select(CrawlLog)

    if company_id is not None:
        query = query.where(CrawlLog.company_id == company_id)
    if status is not None:
        query = query.where(CrawlLog.status == status)

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query) or 0

    # Get paginated results
    query = (
        query.order_by(CrawlLog.started_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    result = await db.execute(query)
    logs = result.scalars().all()

    # Enrich with company names
    items = []
    for log in logs:
        company_name = None
        if log.company_id:
            company = await db.scalar(
                select(Company).where(Company.id == log.company_id)
            )
            company_name = company.name_en if company else None

        log_dict = {**log.__dict__, "company_name": company_name}
        items.append(CrawlLogResponse.model_validate(log_dict))

    return CrawlLogListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/logs/{log_id}", response_model=CrawlLogResponse)
async def get_crawl_log(db: DbSession, log_id: int):
    """크롤링 로그 상세 조회."""
    query = select(CrawlLog).where(CrawlLog.id == log_id)
    result = await db.execute(query)
    log = result.scalar_one_or_none()

    if not log:
        raise HTTPException(status_code=404, detail="Crawl log not found")

    company_name = None
    if log.company_id:
        company = await db.scalar(select(Company).where(Company.id == log.company_id))
        company_name = company.name_en if company else None

    log_dict = {**log.__dict__, "company_name": company_name}
    return CrawlLogResponse.model_validate(log_dict)


@router.get("/schedule", response_model=ScheduleConfig)
async def get_schedule():
    """스케줄 설정 조회."""
    # TODO: Get from database or config
    return ScheduleConfig(
        enabled=True,
        day_of_week=1,
        hour=2,
        minute=0,
        timezone="Asia/Tokyo",
    )


@router.put("/schedule", response_model=ScheduleConfig)
async def update_schedule(data: ScheduleConfig):
    """스케줄 설정 수정."""
    # TODO: Save to database and update scheduler
    return data
