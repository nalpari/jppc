"""Crawl service for managing crawling operations."""

import asyncio
from datetime import datetime
from enum import Enum
from typing import Callable

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crawlers import get_crawler, get_all_crawlers, CrawlResult, PricePlanData
from app.models import Company, PricePlan, PriceHistory, CrawlLog
from app.utils.logger import get_logger

logger = get_logger(__name__)


class CrawlStatus(str, Enum):
    """Crawl job status."""

    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    PARTIAL = "partial"  # Some companies succeeded, some failed
    FAILED = "failed"
    CANCELLED = "cancelled"


class CrawlJob:
    """Represents a crawl job."""

    def __init__(self, job_id: str, company_codes: list[str] | None = None):
        self.job_id = job_id
        self.company_codes = company_codes  # None means all companies
        self.status = CrawlStatus.PENDING
        self.started_at: datetime | None = None
        self.finished_at: datetime | None = None
        self.results: dict[str, CrawlResult] = {}
        self.error: str | None = None

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "job_id": self.job_id,
            "company_codes": self.company_codes,
            "status": self.status.value,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "finished_at": self.finished_at.isoformat() if self.finished_at else None,
            "results": {
                code: {
                    "success": result.success,
                    "plans_count": len(result.plans),
                    "error": result.error_message,
                    "duration": result.duration_seconds,
                }
                for code, result in self.results.items()
            },
            "error": self.error,
        }


class CrawlService:
    """Service for managing crawl operations."""

    def __init__(self):
        self._active_jobs: dict[str, CrawlJob] = {}
        self._job_counter = 0
        self._on_complete_callbacks: list[Callable] = []

    def _generate_job_id(self) -> str:
        """Generate a unique job ID."""
        self._job_counter += 1
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        return f"crawl_{timestamp}_{self._job_counter}"

    def get_active_jobs(self) -> list[CrawlJob]:
        """Get all active crawl jobs."""
        return list(self._active_jobs.values())

    def get_job(self, job_id: str) -> CrawlJob | None:
        """Get a specific job by ID."""
        return self._active_jobs.get(job_id)

    def register_completion_callback(self, callback: Callable) -> None:
        """Register a callback to be called when a crawl completes."""
        self._on_complete_callbacks.append(callback)

    async def start_crawl(
        self,
        db: AsyncSession,
        company_codes: list[str] | None = None,
        headless: bool = True,
    ) -> CrawlJob:
        """Start a new crawl job.

        Args:
            db: Database session
            company_codes: List of company codes to crawl, or None for all
            headless: Whether to run browser in headless mode

        Returns:
            CrawlJob instance
        """
        job = CrawlJob(
            job_id=self._generate_job_id(),
            company_codes=company_codes,
        )
        self._active_jobs[job.job_id] = job

        # Start crawl in background
        asyncio.create_task(self._execute_crawl(db, job, headless))

        return job

    async def _execute_crawl(
        self,
        db: AsyncSession,
        job: CrawlJob,
        headless: bool,
    ) -> None:
        """Execute the crawl job."""
        job.status = CrawlStatus.RUNNING
        job.started_at = datetime.utcnow()

        logger.info(f"Starting crawl job {job.job_id}")

        try:
            # Get crawlers
            if job.company_codes:
                crawlers = [get_crawler(code, headless=headless) for code in job.company_codes]
            else:
                crawlers = get_all_crawlers(headless=headless)

            # Execute crawls
            success_count = 0
            for crawler in crawlers:
                try:
                    async with crawler:
                        result = await crawler.crawl()
                        job.results[crawler.COMPANY_CODE] = result

                        if result.success:
                            success_count += 1
                            # Save results to database
                            await self._save_crawl_results(db, crawler.COMPANY_CODE, result)

                        # Log the crawl
                        await self._log_crawl(db, crawler.COMPANY_CODE, result)

                except Exception as e:
                    logger.error(f"Crawler {crawler.COMPANY_CODE} failed: {e}")
                    job.results[crawler.COMPANY_CODE] = CrawlResult(
                        success=False,
                        company_code=crawler.COMPANY_CODE,
                        error_message=str(e),
                    )

            # Determine final status
            total = len(crawlers)
            if success_count == total:
                job.status = CrawlStatus.SUCCESS
            elif success_count > 0:
                job.status = CrawlStatus.PARTIAL
            else:
                job.status = CrawlStatus.FAILED

        except Exception as e:
            logger.error(f"Crawl job {job.job_id} failed: {e}")
            job.status = CrawlStatus.FAILED
            job.error = str(e)

        finally:
            job.finished_at = datetime.utcnow()
            logger.info(
                f"Crawl job {job.job_id} finished with status {job.status.value}"
            )

            # Call completion callbacks
            for callback in self._on_complete_callbacks:
                try:
                    await callback(job)
                except Exception as e:
                    logger.error(f"Completion callback failed: {e}")

    async def _save_crawl_results(
        self,
        db: AsyncSession,
        company_code: str,
        result: CrawlResult,
    ) -> None:
        """Save crawl results to database."""
        # Get company
        company = await db.scalar(
            select(Company).where(Company.code == company_code)
        )
        if not company:
            logger.warning(f"Company not found: {company_code}")
            return

        for plan_data in result.plans:
            await self._save_price_plan(db, company.id, plan_data)

        await db.commit()

    async def _save_price_plan(
        self,
        db: AsyncSession,
        company_id: int,
        plan_data: PricePlanData,
    ) -> None:
        """Save or update a price plan."""
        # Check if plan exists
        existing = await db.scalar(
            select(PricePlan).where(
                PricePlan.company_id == company_id,
                PricePlan.plan_code == plan_data.plan_code,
            )
        )

        if existing:
            # Check for price changes
            old_prices = {
                "base_charge": existing.base_charge,
                "price_tiers": existing.price_tiers,
            }
            new_prices = {
                "base_charge": plan_data.base_charge,
                "price_tiers": plan_data.unit_prices,
            }

            if old_prices != new_prices:
                # Record price history
                history = PriceHistory(
                    price_plan_id=existing.id,
                    base_charge=existing.base_charge,
                    price_tiers=existing.price_tiers,
                    fuel_adjustment=existing.fuel_adjustment,
                    renewable_surcharge=existing.renewable_surcharge,
                    recorded_at=datetime.utcnow(),
                    change_type="update",
                )
                db.add(history)

                # Update existing plan
                existing.base_charge = plan_data.base_charge
                existing.price_tiers = plan_data.unit_prices
                existing.fuel_adjustment = plan_data.fuel_adjustment
                existing.renewable_surcharge = plan_data.renewable_surcharge
                existing.source_url = plan_data.source_url
                existing.raw_data = plan_data.raw_data
                existing.updated_at = datetime.utcnow()

                logger.info(f"Updated price plan: {plan_data.plan_code}")
            else:
                # Just update timestamp
                existing.updated_at = datetime.utcnow()
        else:
            # Create new plan
            new_plan = PricePlan(
                company_id=company_id,
                plan_name_ja=plan_data.plan_name,
                plan_code=plan_data.plan_code or plan_data.plan_name,
                contract_type=plan_data.contract_type,
                base_charge=plan_data.base_charge,
                price_tiers=plan_data.unit_prices,
                fuel_adjustment=plan_data.fuel_adjustment,
                renewable_surcharge=plan_data.renewable_surcharge,
                effective_date=plan_data.effective_date,
                source_url=plan_data.source_url,
                raw_data=plan_data.raw_data,
                is_current=True,
            )
            db.add(new_plan)
            logger.info(f"Created new price plan: {plan_data.plan_code}")

    async def _log_crawl(
        self,
        db: AsyncSession,
        company_code: str,
        result: CrawlResult,
    ) -> None:
        """Log crawl to database."""
        company = await db.scalar(
            select(Company).where(Company.code == company_code)
        )

        log = CrawlLog(
            company_id=company.id if company else None,
            status="success" if result.success else "failed",
            started_at=result.crawled_at,
            finished_at=datetime.utcnow(),
            duration_seconds=int(result.duration_seconds) if result.duration_seconds else None,
            plans_found=len(result.plans),
            error_message=result.error_message,
        )
        db.add(log)
        await db.commit()

    async def cancel_job(self, job_id: str) -> bool:
        """Cancel a running job."""
        job = self._active_jobs.get(job_id)
        if not job:
            return False

        if job.status == CrawlStatus.RUNNING:
            job.status = CrawlStatus.CANCELLED
            job.finished_at = datetime.utcnow()
            logger.info(f"Cancelled crawl job {job_id}")
            return True

        return False


# Global service instance
crawl_service = CrawlService()
