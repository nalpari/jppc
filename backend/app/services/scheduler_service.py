"""Scheduler service for automated crawling."""

from datetime import datetime
from typing import Any, Callable

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.executors.asyncio import AsyncIOExecutor

from app.config import get_settings
from app.utils.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()


class SchedulerService:
    """Service for managing scheduled crawl jobs."""

    def __init__(self):
        self._scheduler: AsyncIOScheduler | None = None
        self._is_running = False
        self._crawl_callback: Callable | None = None

    def configure(
        self,
        crawl_callback: Callable,
    ) -> None:
        """Configure the scheduler with crawl callback.

        Args:
            crawl_callback: Async function to call when crawl is triggered
        """
        self._crawl_callback = crawl_callback

        jobstores = {"default": MemoryJobStore()}
        executors = {"default": AsyncIOExecutor()}
        job_defaults = {
            "coalesce": True,  # Combine missed runs into one
            "max_instances": 1,  # Only one instance at a time
            "misfire_grace_time": 3600,  # 1 hour grace time
        }

        self._scheduler = AsyncIOScheduler(
            jobstores=jobstores,
            executors=executors,
            job_defaults=job_defaults,
            timezone="Asia/Tokyo",
        )

    def start(self) -> None:
        """Start the scheduler."""
        if not self._scheduler:
            raise RuntimeError("Scheduler not configured. Call configure() first.")

        if self._is_running:
            logger.warning("Scheduler already running")
            return

        self._scheduler.start()
        self._is_running = True
        logger.info("Scheduler started")

    def stop(self) -> None:
        """Stop the scheduler."""
        if self._scheduler and self._is_running:
            self._scheduler.shutdown(wait=False)
            self._is_running = False
            logger.info("Scheduler stopped")

    @property
    def is_running(self) -> bool:
        """Check if scheduler is running."""
        return self._is_running

    def add_weekly_crawl(
        self,
        day_of_week: int = 0,  # 0 = Monday
        hour: int = 3,  # 3 AM
        minute: int = 0,
        company_codes: list[str] | None = None,
    ) -> str:
        """Add a weekly crawl job.

        Args:
            day_of_week: Day of week (0=Monday, 6=Sunday)
            hour: Hour to run (0-23)
            minute: Minute to run (0-59)
            company_codes: Specific companies to crawl, or None for all

        Returns:
            Job ID
        """
        if not self._scheduler:
            raise RuntimeError("Scheduler not configured")

        job_id = f"weekly_crawl_{day_of_week}_{hour:02d}{minute:02d}"

        # Remove existing job if any
        if self._scheduler.get_job(job_id):
            self._scheduler.remove_job(job_id)

        # Create cron trigger
        trigger = CronTrigger(
            day_of_week=day_of_week,
            hour=hour,
            minute=minute,
            timezone="Asia/Tokyo",
        )

        # Add job
        self._scheduler.add_job(
            self._execute_scheduled_crawl,
            trigger=trigger,
            id=job_id,
            kwargs={"company_codes": company_codes},
            name=f"Weekly crawl at {hour:02d}:{minute:02d} on day {day_of_week}",
        )

        logger.info(f"Added weekly crawl job: {job_id}")
        return job_id

    def add_daily_crawl(
        self,
        hour: int = 3,
        minute: int = 0,
        company_codes: list[str] | None = None,
    ) -> str:
        """Add a daily crawl job.

        Args:
            hour: Hour to run (0-23)
            minute: Minute to run (0-59)
            company_codes: Specific companies to crawl, or None for all

        Returns:
            Job ID
        """
        if not self._scheduler:
            raise RuntimeError("Scheduler not configured")

        job_id = f"daily_crawl_{hour:02d}{minute:02d}"

        if self._scheduler.get_job(job_id):
            self._scheduler.remove_job(job_id)

        trigger = CronTrigger(
            hour=hour,
            minute=minute,
            timezone="Asia/Tokyo",
        )

        self._scheduler.add_job(
            self._execute_scheduled_crawl,
            trigger=trigger,
            id=job_id,
            kwargs={"company_codes": company_codes},
            name=f"Daily crawl at {hour:02d}:{minute:02d}",
        )

        logger.info(f"Added daily crawl job: {job_id}")
        return job_id

    def add_interval_crawl(
        self,
        hours: int = 24,
        company_codes: list[str] | None = None,
    ) -> str:
        """Add an interval-based crawl job.

        Args:
            hours: Interval in hours
            company_codes: Specific companies to crawl, or None for all

        Returns:
            Job ID
        """
        if not self._scheduler:
            raise RuntimeError("Scheduler not configured")

        job_id = f"interval_crawl_{hours}h"

        if self._scheduler.get_job(job_id):
            self._scheduler.remove_job(job_id)

        self._scheduler.add_job(
            self._execute_scheduled_crawl,
            "interval",
            hours=hours,
            id=job_id,
            kwargs={"company_codes": company_codes},
            name=f"Interval crawl every {hours} hours",
        )

        logger.info(f"Added interval crawl job: {job_id}")
        return job_id

    def remove_job(self, job_id: str) -> bool:
        """Remove a scheduled job.

        Args:
            job_id: Job ID to remove

        Returns:
            True if removed, False if not found
        """
        if not self._scheduler:
            return False

        job = self._scheduler.get_job(job_id)
        if job:
            self._scheduler.remove_job(job_id)
            logger.info(f"Removed job: {job_id}")
            return True
        return False

    def get_jobs(self) -> list[dict[str, Any]]:
        """Get all scheduled jobs.

        Returns:
            List of job information dictionaries
        """
        if not self._scheduler:
            return []

        jobs = []
        for job in self._scheduler.get_jobs():
            next_run = job.next_run_time
            jobs.append(
                {
                    "id": job.id,
                    "name": job.name,
                    "next_run": next_run.isoformat() if next_run else None,
                    "trigger": str(job.trigger),
                }
            )
        return jobs

    def get_job(self, job_id: str) -> dict[str, Any] | None:
        """Get a specific job.

        Args:
            job_id: Job ID

        Returns:
            Job information dictionary or None
        """
        if not self._scheduler:
            return None

        job = self._scheduler.get_job(job_id)
        if not job:
            return None

        next_run = job.next_run_time
        return {
            "id": job.id,
            "name": job.name,
            "next_run": next_run.isoformat() if next_run else None,
            "trigger": str(job.trigger),
        }

    def pause_job(self, job_id: str) -> bool:
        """Pause a job."""
        if not self._scheduler:
            return False

        job = self._scheduler.get_job(job_id)
        if job:
            self._scheduler.pause_job(job_id)
            return True
        return False

    def resume_job(self, job_id: str) -> bool:
        """Resume a paused job."""
        if not self._scheduler:
            return False

        job = self._scheduler.get_job(job_id)
        if job:
            self._scheduler.resume_job(job_id)
            return True
        return False

    async def _execute_scheduled_crawl(
        self,
        company_codes: list[str] | None = None,
    ) -> None:
        """Execute a scheduled crawl.

        Args:
            company_codes: Companies to crawl
        """
        logger.info(f"Executing scheduled crawl for: {company_codes or 'all'}")

        if self._crawl_callback:
            try:
                await self._crawl_callback(company_codes)
            except Exception as e:
                logger.error(f"Scheduled crawl failed: {e}")
        else:
            logger.warning("No crawl callback configured")

    def trigger_job_now(self, job_id: str) -> bool:
        """Trigger a job to run immediately.

        Args:
            job_id: Job ID to trigger

        Returns:
            True if triggered, False if not found
        """
        if not self._scheduler:
            return False

        job = self._scheduler.get_job(job_id)
        if job:
            self._scheduler.modify_job(job_id, next_run_time=datetime.now())
            return True
        return False


# Global service instance
scheduler_service = SchedulerService()
