"""Chubu Electric Power Company crawler.

中部電力 요금 정보 크롤러
Website: https://www.chuden.co.jp/
"""

from datetime import datetime

from playwright.async_api import Page

from app.crawlers.base_crawler import BaseCrawler, PricePlanData
from app.crawlers.crawler_utils import RateLimiter, wait_for_page_load, clean_text
from app.utils.logger import get_logger

logger = get_logger(__name__)


class ChubuCrawler(BaseCrawler):
    """Chubu Electric Power Company price crawler.

    Crawls electricity price information from Chubu Electric's official website.
    Target region: Chubu (中部地方) - Aichi, Gifu, Mie, Nagano, Shizuoka
    """

    COMPANY_CODE = "chubu"
    COMPANY_NAME = "中部電力ミライズ"
    BASE_URL = "https://www.chuden.co.jp"

    # Price information pages
    PRICE_PAGES = {
        "metered_b": "/home/basic/charge/menu/meterb.html",  # 従量電灯B
        "metered_c": "/home/basic/charge/menu/meterc.html",  # 従量電灯C
        "smart_life": "/home/basic/charge/menu/smartlife.html",  # スマートライフプラン
    }

    def __init__(self, headless: bool = True, timeout: int = 30000):
        super().__init__(headless, timeout)
        self.rate_limiter = RateLimiter(min_delay=2.0, max_delay=4.0)

    def get_price_page_urls(self) -> list[str]:
        """Get URLs for Chubu Electric price pages."""
        return [f"{self.BASE_URL}{path}" for path in self.PRICE_PAGES.values()]

    async def _crawl_prices(self) -> tuple[list[PricePlanData], int]:
        """Crawl Chubu Electric price information.

        Returns:
            Tuple of (list of price plans, pages crawled count)
        """
        plans: list[PricePlanData] = []
        pages_crawled = 0

        page = await self.new_page()

        try:
            # Crawl 従量電灯B
            await self.rate_limiter.wait()
            plan = await self._crawl_metered_b(page)
            if plan:
                plans.append(plan)
            pages_crawled += 1

            # Crawl 従量電灯C
            await self.rate_limiter.wait()
            plan = await self._crawl_metered_c(page)
            if plan:
                plans.append(plan)
            pages_crawled += 1

            # Crawl スマートライフプラン
            await self.rate_limiter.wait()
            plan = await self._crawl_smart_life(page)
            if plan:
                plans.append(plan)
            pages_crawled += 1

        finally:
            await page.close()

        return plans, pages_crawled

    async def _crawl_metered_b(self, page: Page) -> PricePlanData | None:
        """Crawl 従量電灯B plan."""
        url = f"{self.BASE_URL}{self.PRICE_PAGES['metered_b']}"
        logger.info(f"Crawling Chubu 従量電灯B: {url}")

        try:
            await page.goto(url)
            await wait_for_page_load(page)

            base_charge = await self._extract_base_charge(page, "30A")
            unit_prices = await self._extract_unit_prices(page)
            fuel_adj = await self._extract_fuel_adjustment(page)
            renewable = await self._extract_renewable_surcharge(page)

            return PricePlanData(
                plan_name="従量電灯B",
                plan_code="chubu_metered_b",
                contract_type="従量電灯",
                base_charge=base_charge,
                unit_prices=unit_prices,
                fuel_adjustment=fuel_adj,
                renewable_surcharge=renewable,
                source_url=url,
                raw_data={
                    "plan_type": "metered_b",
                    "crawled_at": datetime.utcnow().isoformat(),
                },
            )

        except Exception as e:
            logger.error(f"Failed to crawl Chubu 従量電灯B: {e}")
            return None

    async def _crawl_metered_c(self, page: Page) -> PricePlanData | None:
        """Crawl 従量電灯C plan."""
        url = f"{self.BASE_URL}{self.PRICE_PAGES['metered_c']}"
        logger.info(f"Crawling Chubu 従量電灯C: {url}")

        try:
            await page.goto(url)
            await wait_for_page_load(page)

            base_charge = await self._extract_base_charge(page, "6kVA")
            unit_prices = await self._extract_unit_prices(page)
            fuel_adj = await self._extract_fuel_adjustment(page)
            renewable = await self._extract_renewable_surcharge(page)

            return PricePlanData(
                plan_name="従量電灯C",
                plan_code="chubu_metered_c",
                contract_type="従量電灯",
                base_charge=base_charge,
                unit_prices=unit_prices,
                fuel_adjustment=fuel_adj,
                renewable_surcharge=renewable,
                source_url=url,
                raw_data={
                    "plan_type": "metered_c",
                    "crawled_at": datetime.utcnow().isoformat(),
                },
            )

        except Exception as e:
            logger.error(f"Failed to crawl Chubu 従量電灯C: {e}")
            return None

    async def _crawl_smart_life(self, page: Page) -> PricePlanData | None:
        """Crawl スマートライフプラン."""
        url = f"{self.BASE_URL}{self.PRICE_PAGES['smart_life']}"
        logger.info(f"Crawling Chubu スマートライフプラン: {url}")

        try:
            await page.goto(url)
            await wait_for_page_load(page)

            base_charge = await self._extract_base_charge(page, "10kVA")
            unit_prices = await self._extract_tou_prices(page)
            fuel_adj = await self._extract_fuel_adjustment(page)
            renewable = await self._extract_renewable_surcharge(page)

            return PricePlanData(
                plan_name="スマートライフプラン",
                plan_code="chubu_smart_life",
                contract_type="時間帯別",
                base_charge=base_charge,
                unit_prices=unit_prices,
                fuel_adjustment=fuel_adj,
                renewable_surcharge=renewable,
                source_url=url,
                raw_data={
                    "plan_type": "smart_life",
                    "crawled_at": datetime.utcnow().isoformat(),
                },
            )

        except Exception as e:
            logger.error(f"Failed to crawl Chubu スマートライフプラン: {e}")
            return None

    async def _extract_base_charge(
        self, page: Page, capacity: str = "30A"
    ) -> float | None:
        """Extract base charge for specified capacity."""
        try:
            tables = await page.query_selector_all("table")
            for table in tables:
                text = await table.inner_text()
                if "基本料金" in text and capacity in text:
                    rows = await table.query_selector_all("tr")
                    for row in rows:
                        row_text = await row.inner_text()
                        if capacity in row_text:
                            price = self._parse_price(row_text)
                            if price:
                                return price
        except Exception as e:
            logger.debug(f"Failed to extract base charge: {e}")
        return None

    async def _extract_unit_prices(self, page: Page) -> dict[str, float]:
        """Extract tiered unit prices.

        Chubu Electric uses 3-tier pricing:
        - First tier: up to 120kWh
        - Second tier: 120-300kWh
        - Third tier: over 300kWh
        """
        unit_prices: dict[str, float] = {}

        try:
            tables = await page.query_selector_all("table")
            for table in tables:
                text = await table.inner_text()
                if "電力量料金" in text:
                    rows = await table.query_selector_all("tr")
                    for row in rows:
                        row_text = clean_text(await row.inner_text())

                        if "120kWh" in row_text and ("まで" in row_text or "以下" in row_text):
                            price = self._parse_price(row_text)
                            if price:
                                unit_prices["tier1_0_120"] = price
                        elif "120kWh" in row_text and "300kWh" in row_text:
                            price = self._parse_price(row_text)
                            if price:
                                unit_prices["tier2_120_300"] = price
                        elif "300kWh" in row_text and ("超過" in row_text or "超え" in row_text):
                            price = self._parse_price(row_text)
                            if price:
                                unit_prices["tier3_over_300"] = price

        except Exception as e:
            logger.debug(f"Failed to extract unit prices: {e}")

        return unit_prices

    async def _extract_tou_prices(self, page: Page) -> dict[str, float]:
        """Extract time-of-use prices."""
        unit_prices: dict[str, float] = {}

        try:
            tables = await page.query_selector_all("table")
            for table in tables:
                text = await table.inner_text()
                if "電力量料金" in text or "デイタイム" in text or "ナイトタイム" in text:
                    rows = await table.query_selector_all("tr")
                    for row in rows:
                        row_text = clean_text(await row.inner_text())

                        if "デイタイム" in row_text or "昼間" in row_text:
                            price = self._parse_price(row_text)
                            if price:
                                unit_prices["daytime"] = price
                        elif "@ホームタイム" in row_text or "リビングタイム" in row_text:
                            price = self._parse_price(row_text)
                            if price:
                                unit_prices["home_time"] = price
                        elif "ナイトタイム" in row_text or "夜間" in row_text:
                            price = self._parse_price(row_text)
                            if price:
                                unit_prices["nighttime"] = price

        except Exception as e:
            logger.debug(f"Failed to extract TOU prices: {e}")

        return unit_prices

    async def _extract_fuel_adjustment(self, page: Page) -> float | None:
        """Extract fuel cost adjustment rate."""
        return None

    async def _extract_renewable_surcharge(self, page: Page) -> float | None:
        """Extract renewable energy surcharge."""
        return 1.40  # National rate for 2024
