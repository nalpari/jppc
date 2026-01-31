"""Base crawler abstract class for power company crawlers."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from playwright.async_api import Browser, BrowserContext, Page, async_playwright

from app.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class PricePlanData:
    """Extracted price plan data structure."""

    plan_name: str
    plan_code: str | None = None
    contract_type: str | None = None  # 従量電灯A, 従量電灯B, etc.
    base_charge: float | None = None  # 基本料金 (円)
    unit_prices: dict[str, float] = field(default_factory=dict)  # 従量料金 (段階別)
    minimum_charge: float | None = None  # 最低料金
    fuel_adjustment: float | None = None  # 燃料費調整単価
    renewable_surcharge: float | None = None  # 再エネ賦課金
    effective_date: datetime | None = None  # 適用開始日
    source_url: str | None = None
    raw_data: dict[str, Any] = field(default_factory=dict)  # Original scraped data


@dataclass
class CrawlResult:
    """Result of a crawl operation."""

    success: bool
    company_code: str
    plans: list[PricePlanData] = field(default_factory=list)
    error_message: str | None = None
    crawled_at: datetime = field(default_factory=datetime.utcnow)
    duration_seconds: float = 0.0
    pages_crawled: int = 0


class BaseCrawler(ABC):
    """Abstract base class for power company crawlers.

    All power company crawlers should inherit from this class and implement
    the abstract methods for company-specific crawling logic.
    """

    # Class-level configuration
    COMPANY_CODE: str = ""
    COMPANY_NAME: str = ""
    BASE_URL: str = ""
    RATE_LIMIT_DELAY: float = 2.0  # seconds between requests

    def __init__(self, headless: bool = True, timeout: int = 30000):
        """Initialize the crawler.

        Args:
            headless: Whether to run browser in headless mode
            timeout: Default timeout for page operations in milliseconds
        """
        self.headless = headless
        self.timeout = timeout
        self._browser: Browser | None = None
        self._context: BrowserContext | None = None
        self._playwright = None

    async def __aenter__(self):
        """Async context manager entry."""
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.stop()

    async def start(self) -> None:
        """Start the browser instance."""
        logger.info(f"Starting {self.COMPANY_NAME} crawler...")
        self._playwright = await async_playwright().start()
        self._browser = await self._playwright.chromium.launch(
            headless=self.headless,
        )
        self._context = await self._browser.new_context(
            user_agent=self._get_user_agent(),
            locale="ja-JP",
            timezone_id="Asia/Tokyo",
        )
        self._context.set_default_timeout(self.timeout)
        logger.info(f"{self.COMPANY_NAME} crawler started")

    async def stop(self) -> None:
        """Stop the browser instance."""
        if self._context:
            await self._context.close()
        if self._browser:
            await self._browser.close()
        if self._playwright:
            await self._playwright.stop()
        logger.info(f"{self.COMPANY_NAME} crawler stopped")

    def _get_user_agent(self) -> str:
        """Get a realistic user agent string."""
        return (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )

    async def new_page(self) -> Page:
        """Create a new browser page."""
        if not self._context:
            raise RuntimeError("Crawler not started. Call start() first.")
        return await self._context.new_page()

    async def crawl(self) -> CrawlResult:
        """Execute the crawl operation.

        Returns:
            CrawlResult with extracted data or error information
        """
        start_time = datetime.utcnow()
        pages_crawled = 0

        try:
            logger.info(f"Starting crawl for {self.COMPANY_NAME}")

            # Execute company-specific crawl logic
            plans, pages_crawled = await self._crawl_prices()

            duration = (datetime.utcnow() - start_time).total_seconds()
            logger.info(
                f"Crawl completed for {self.COMPANY_NAME}: "
                f"{len(plans)} plans found in {duration:.1f}s"
            )

            return CrawlResult(
                success=True,
                company_code=self.COMPANY_CODE,
                plans=plans,
                duration_seconds=duration,
                pages_crawled=pages_crawled,
            )

        except Exception as e:
            duration = (datetime.utcnow() - start_time).total_seconds()
            error_msg = str(e)
            logger.error(f"Crawl failed for {self.COMPANY_NAME}: {error_msg}")

            return CrawlResult(
                success=False,
                company_code=self.COMPANY_CODE,
                error_message=error_msg,
                duration_seconds=duration,
                pages_crawled=pages_crawled,
            )

    @abstractmethod
    async def _crawl_prices(self) -> tuple[list[PricePlanData], int]:
        """Company-specific crawl implementation.

        Returns:
            Tuple of (list of extracted plans, number of pages crawled)
        """
        pass

    @abstractmethod
    def get_price_page_urls(self) -> list[str]:
        """Get the URLs of pages containing price information.

        Returns:
            List of URLs to crawl
        """
        pass

    async def _safe_get_text(self, page: Page, selector: str) -> str | None:
        """Safely extract text from an element."""
        try:
            element = await page.query_selector(selector)
            if element:
                return (await element.inner_text()).strip()
        except Exception as e:
            logger.debug(f"Failed to get text for {selector}: {e}")
        return None

    async def _safe_get_attribute(
        self, page: Page, selector: str, attribute: str
    ) -> str | None:
        """Safely extract an attribute from an element."""
        try:
            element = await page.query_selector(selector)
            if element:
                return await element.get_attribute(attribute)
        except Exception as e:
            logger.debug(f"Failed to get attribute {attribute} for {selector}: {e}")
        return None

    def _parse_price(self, text: str | None) -> float | None:
        """Parse a Japanese price string to float.

        Handles formats like:
        - "1,234円" -> 1234.0
        - "1,234.56円/kWh" -> 1234.56
        - "¥1,234" -> 1234.0
        """
        if not text:
            return None

        import re

        # Remove currency symbols and units
        cleaned = re.sub(r"[円¥/kWh（）\(\)\s]", "", text)
        # Remove commas
        cleaned = cleaned.replace(",", "")
        # Extract number
        match = re.search(r"[\d.]+", cleaned)
        if match:
            try:
                return float(match.group())
            except ValueError:
                pass
        return None
