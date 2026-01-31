"""Tokyo Electric Power Company (TEPCO) crawler.

도쿄전력 요금 정보 크롤러
Website: https://www.tepco.co.jp/
"""

import asyncio
from datetime import datetime

from playwright.async_api import Page

from app.crawlers.base_crawler import BaseCrawler, PricePlanData
from app.crawlers.crawler_utils import RateLimiter, wait_for_page_load, clean_text
from app.utils.logger import get_logger

logger = get_logger(__name__)


class TEPCOCrawler(BaseCrawler):
    """Tokyo Electric Power Company (TEPCO) price crawler.

    Crawls electricity price information from TEPCO's official website.
    Target region: Kanto (関東地方)
    """

    COMPANY_CODE = "tepco"
    COMPANY_NAME = "東京電力エナジーパートナー"
    BASE_URL = "https://www.tepco.co.jp"

    # Price information pages
    PRICE_PAGES = {
        "metered_a": "/ep/private/plan/standard/chargelist01.html",  # 従量電灯B
        "metered_b": "/ep/private/plan/standard/chargelist02.html",  # 従量電灯C
        "smart_life": "/ep/private/plan/smartlife/chargelist.html",  # スマートライフ
    }

    def __init__(self, headless: bool = True, timeout: int = 30000):
        super().__init__(headless, timeout)
        self.rate_limiter = RateLimiter(min_delay=2.0, max_delay=4.0)

    def get_price_page_urls(self) -> list[str]:
        """Get URLs for TEPCO price pages."""
        return [f"{self.BASE_URL}{path}" for path in self.PRICE_PAGES.values()]

    async def _crawl_prices(self) -> tuple[list[PricePlanData], int]:
        """Crawl TEPCO price information.

        Returns:
            Tuple of (list of price plans, pages crawled count)
        """
        plans: list[PricePlanData] = []
        pages_crawled = 0

        page = await self.new_page()

        try:
            # Crawl 従量電灯B (Metered Lighting B)
            await self.rate_limiter.wait()
            plan = await self._crawl_metered_b(page)
            if plan:
                plans.append(plan)
            pages_crawled += 1

            # Crawl 従量電灯C (Metered Lighting C)
            await self.rate_limiter.wait()
            plan = await self._crawl_metered_c(page)
            if plan:
                plans.append(plan)
            pages_crawled += 1

            # Crawl スマートライフ (Smart Life)
            await self.rate_limiter.wait()
            plan = await self._crawl_smart_life(page)
            if plan:
                plans.append(plan)
            pages_crawled += 1

        finally:
            await page.close()

        return plans, pages_crawled

    async def _crawl_metered_b(self, page: Page) -> PricePlanData | None:
        """Crawl 従量電灯B plan.

        This is the most common residential plan in TEPCO area.
        """
        url = f"{self.BASE_URL}{self.PRICE_PAGES['metered_a']}"
        logger.info(f"Crawling TEPCO 従量電灯B: {url}")

        try:
            await page.goto(url)
            await wait_for_page_load(page)

            # Extract base charge (基本料金)
            base_charge = await self._extract_base_charge(page)

            # Extract unit prices (従量料金)
            unit_prices = await self._extract_unit_prices(page)

            # Extract fuel adjustment and renewable surcharge
            fuel_adj = await self._extract_fuel_adjustment(page)
            renewable = await self._extract_renewable_surcharge(page)

            return PricePlanData(
                plan_name="従量電灯B",
                plan_code="tepco_metered_b",
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
            logger.error(f"Failed to crawl TEPCO 従量電灯B: {e}")
            return None

    async def _crawl_metered_c(self, page: Page) -> PricePlanData | None:
        """Crawl 従量電灯C plan.

        For larger residential/small commercial customers.
        """
        url = f"{self.BASE_URL}{self.PRICE_PAGES['metered_b']}"
        logger.info(f"Crawling TEPCO 従量電灯C: {url}")

        try:
            await page.goto(url)
            await wait_for_page_load(page)

            base_charge = await self._extract_base_charge(page)
            unit_prices = await self._extract_unit_prices(page)
            fuel_adj = await self._extract_fuel_adjustment(page)
            renewable = await self._extract_renewable_surcharge(page)

            return PricePlanData(
                plan_name="従量電灯C",
                plan_code="tepco_metered_c",
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
            logger.error(f"Failed to crawl TEPCO 従量電灯C: {e}")
            return None

    async def _crawl_smart_life(self, page: Page) -> PricePlanData | None:
        """Crawl スマートライフ plan.

        Time-of-use pricing plan.
        """
        url = f"{self.BASE_URL}{self.PRICE_PAGES['smart_life']}"
        logger.info(f"Crawling TEPCO スマートライフ: {url}")

        try:
            await page.goto(url)
            await wait_for_page_load(page)

            base_charge = await self._extract_base_charge(page)
            unit_prices = await self._extract_tou_prices(page)
            fuel_adj = await self._extract_fuel_adjustment(page)
            renewable = await self._extract_renewable_surcharge(page)

            return PricePlanData(
                plan_name="スマートライフS",
                plan_code="tepco_smart_life_s",
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
            logger.error(f"Failed to crawl TEPCO スマートライフ: {e}")
            return None

    async def _extract_base_charge(self, page: Page) -> float | None:
        """Extract base charge from page.

        TEPCO typically shows base charge per ampere (10A, 15A, 20A, etc.)
        We extract the 30A rate as the reference.
        """
        try:
            # Look for table with base charge information
            tables = await page.query_selector_all("table")
            for table in tables:
                text = await table.inner_text()
                if "基本料金" in text and "30A" in text:
                    # Find the row with 30A
                    rows = await table.query_selector_all("tr")
                    for row in rows:
                        row_text = await row.inner_text()
                        if "30A" in row_text:
                            # Extract the price
                            price = self._parse_price(row_text)
                            if price:
                                return price
        except Exception as e:
            logger.debug(f"Failed to extract base charge: {e}")
        return None

    async def _extract_unit_prices(self, page: Page) -> dict[str, float]:
        """Extract tiered unit prices (従量料金).

        TEPCO uses 3-tier pricing:
        - First tier: up to 120kWh
        - Second tier: 120-300kWh
        - Third tier: over 300kWh
        """
        unit_prices: dict[str, float] = {}

        try:
            tables = await page.query_selector_all("table")
            for table in tables:
                text = await table.inner_text()
                if "電力量料金" in text or "従量料金" in text:
                    rows = await table.query_selector_all("tr")
                    for row in rows:
                        row_text = clean_text(await row.inner_text())

                        # First tier (第1段階)
                        if "120kWh" in row_text and "まで" in row_text:
                            price = self._parse_price(row_text)
                            if price:
                                unit_prices["tier1_0_120"] = price

                        # Second tier (第2段階)
                        elif "120kWh" in row_text and "300kWh" in row_text:
                            price = self._parse_price(row_text)
                            if price:
                                unit_prices["tier2_120_300"] = price

                        # Third tier (第3段階)
                        elif "300kWh" in row_text and "超過" in row_text:
                            price = self._parse_price(row_text)
                            if price:
                                unit_prices["tier3_over_300"] = price

        except Exception as e:
            logger.debug(f"Failed to extract unit prices: {e}")

        return unit_prices

    async def _extract_tou_prices(self, page: Page) -> dict[str, float]:
        """Extract time-of-use prices for smart life plan."""
        unit_prices: dict[str, float] = {}

        try:
            tables = await page.query_selector_all("table")
            for table in tables:
                text = await table.inner_text()
                if "電力量料金" in text:
                    rows = await table.query_selector_all("tr")
                    for row in rows:
                        row_text = clean_text(await row.inner_text())

                        # Daytime rate
                        if "昼間" in row_text or "6時" in row_text:
                            price = self._parse_price(row_text)
                            if price:
                                unit_prices["daytime"] = price

                        # Nighttime rate
                        elif "夜間" in row_text or "1時" in row_text:
                            price = self._parse_price(row_text)
                            if price:
                                unit_prices["nighttime"] = price

        except Exception as e:
            logger.debug(f"Failed to extract TOU prices: {e}")

        return unit_prices

    async def _extract_fuel_adjustment(self, page: Page) -> float | None:
        """Extract fuel cost adjustment rate."""
        try:
            text = await page.inner_text("body")
            if "燃料費調整" in text:
                # This is typically on a separate page or updated monthly
                # For now, return None - will be updated in actual implementation
                return None
        except Exception:
            pass
        return None

    async def _extract_renewable_surcharge(self, page: Page) -> float | None:
        """Extract renewable energy surcharge."""
        try:
            text = await page.inner_text("body")
            if "再エネ賦課金" in text or "再生可能エネルギー" in text:
                # This is set nationally and updated annually
                # Current rate as of 2024: 1.40 yen/kWh
                return 1.40
        except Exception:
            pass
        return None
