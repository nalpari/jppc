"""Chugoku Electric Power Company crawler.

中国電力 요금 정보 크롤러
Website: https://www.energia.co.jp/
"""

from datetime import datetime

from playwright.async_api import Page

from app.crawlers.base_crawler import BaseCrawler, PricePlanData
from app.crawlers.crawler_utils import RateLimiter, wait_for_page_load, clean_text
from app.utils.logger import get_logger

logger = get_logger(__name__)


class ChugokuCrawler(BaseCrawler):
    """Chugoku Electric Power Company price crawler.

    Crawls electricity price information from Chugoku Electric's official website.
    Target region: Chugoku (中国地方) - Hiroshima, Okayama, Yamaguchi, Tottori, Shimane
    """

    COMPANY_CODE = "chugoku"
    COMPANY_NAME = "中国電力"
    BASE_URL = "https://www.energia.co.jp"

    # Price information pages
    PRICE_PAGES = {
        "metered_a": "/elec/personal/menu/juryo-a/",  # 従量電灯A
        "metered_b": "/elec/personal/menu/juryo-b/",  # 従量電灯B
        "electric_delight": "/elec/personal/menu/electric-delight/",  # ぐっとずっと。プラン
    }

    def __init__(self, headless: bool = True, timeout: int = 30000):
        super().__init__(headless, timeout)
        self.rate_limiter = RateLimiter(min_delay=2.0, max_delay=4.0)

    def get_price_page_urls(self) -> list[str]:
        """Get URLs for Chugoku Electric price pages."""
        return [f"{self.BASE_URL}{path}" for path in self.PRICE_PAGES.values()]

    async def _crawl_prices(self) -> tuple[list[PricePlanData], int]:
        """Crawl Chugoku Electric price information.

        Returns:
            Tuple of (list of price plans, pages crawled count)
        """
        plans: list[PricePlanData] = []
        pages_crawled = 0

        page = await self.new_page()

        try:
            # Crawl 従量電灯A
            await self.rate_limiter.wait()
            plan = await self._crawl_metered_a(page)
            if plan:
                plans.append(plan)
            pages_crawled += 1

            # Crawl 従量電灯B
            await self.rate_limiter.wait()
            plan = await self._crawl_metered_b(page)
            if plan:
                plans.append(plan)
            pages_crawled += 1

            # Crawl ぐっとずっと。プラン
            await self.rate_limiter.wait()
            plan = await self._crawl_electric_delight(page)
            if plan:
                plans.append(plan)
            pages_crawled += 1

        finally:
            await page.close()

        return plans, pages_crawled

    async def _crawl_metered_a(self, page: Page) -> PricePlanData | None:
        """Crawl 従量電灯A plan.

        For small residential customers with minimum charge.
        """
        url = f"{self.BASE_URL}{self.PRICE_PAGES['metered_a']}"
        logger.info(f"Crawling Chugoku 従量電灯A: {url}")

        try:
            await page.goto(url)
            await wait_for_page_load(page)

            minimum_charge = await self._extract_minimum_charge(page)
            unit_prices = await self._extract_unit_prices_a(page)
            fuel_adj = await self._extract_fuel_adjustment(page)
            renewable = await self._extract_renewable_surcharge(page)

            return PricePlanData(
                plan_name="従量電灯A",
                plan_code="chugoku_metered_a",
                contract_type="従量電灯",
                minimum_charge=minimum_charge,
                unit_prices=unit_prices,
                fuel_adjustment=fuel_adj,
                renewable_surcharge=renewable,
                source_url=url,
                raw_data={
                    "plan_type": "metered_a",
                    "crawled_at": datetime.utcnow().isoformat(),
                },
            )

        except Exception as e:
            logger.error(f"Failed to crawl Chugoku 従量電灯A: {e}")
            return None

    async def _crawl_metered_b(self, page: Page) -> PricePlanData | None:
        """Crawl 従量電灯B plan."""
        url = f"{self.BASE_URL}{self.PRICE_PAGES['metered_b']}"
        logger.info(f"Crawling Chugoku 従量電灯B: {url}")

        try:
            await page.goto(url)
            await wait_for_page_load(page)

            base_charge = await self._extract_base_charge(page)
            unit_prices = await self._extract_unit_prices_b(page)
            fuel_adj = await self._extract_fuel_adjustment(page)
            renewable = await self._extract_renewable_surcharge(page)

            return PricePlanData(
                plan_name="従量電灯B",
                plan_code="chugoku_metered_b",
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
            logger.error(f"Failed to crawl Chugoku 従量電灯B: {e}")
            return None

    async def _crawl_electric_delight(self, page: Page) -> PricePlanData | None:
        """Crawl ぐっとずっと。プラン (Electric Delight plan).

        Discount plan for residential customers.
        """
        url = f"{self.BASE_URL}{self.PRICE_PAGES['electric_delight']}"
        logger.info(f"Crawling Chugoku ぐっとずっと。プラン: {url}")

        try:
            await page.goto(url)
            await wait_for_page_load(page)

            minimum_charge = await self._extract_minimum_charge(page)
            unit_prices = await self._extract_electric_delight_prices(page)
            fuel_adj = await self._extract_fuel_adjustment(page)
            renewable = await self._extract_renewable_surcharge(page)

            return PricePlanData(
                plan_name="ぐっとずっと。プラン スマートコース",
                plan_code="chugoku_electric_delight_smart",
                contract_type="定額",
                minimum_charge=minimum_charge,
                unit_prices=unit_prices,
                fuel_adjustment=fuel_adj,
                renewable_surcharge=renewable,
                source_url=url,
                raw_data={
                    "plan_type": "electric_delight",
                    "crawled_at": datetime.utcnow().isoformat(),
                },
            )

        except Exception as e:
            logger.error(f"Failed to crawl Chugoku ぐっとずっと。プラン: {e}")
            return None

    async def _extract_minimum_charge(self, page: Page) -> float | None:
        """Extract minimum charge."""
        try:
            tables = await page.query_selector_all("table")
            for table in tables:
                text = await table.inner_text()
                if "最低料金" in text:
                    rows = await table.query_selector_all("tr")
                    for row in rows:
                        row_text = await row.inner_text()
                        if "最低料金" in row_text:
                            price = self._parse_price(row_text)
                            if price:
                                return price
        except Exception as e:
            logger.debug(f"Failed to extract minimum charge: {e}")
        return None

    async def _extract_base_charge(self, page: Page) -> float | None:
        """Extract base charge."""
        try:
            tables = await page.query_selector_all("table")
            for table in tables:
                text = await table.inner_text()
                if "基本料金" in text:
                    rows = await table.query_selector_all("tr")
                    for row in rows:
                        row_text = await row.inner_text()
                        if "1kVA" in row_text:
                            price = self._parse_price(row_text)
                            if price:
                                return price
        except Exception as e:
            logger.debug(f"Failed to extract base charge: {e}")
        return None

    async def _extract_unit_prices_a(self, page: Page) -> dict[str, float]:
        """Extract tiered unit prices for 従量電灯A.

        Chugoku Electric uses similar tiering to KEPCO:
        - First 15kWh included in minimum charge
        - 15-120kWh: first tier
        - 120-300kWh: second tier
        - Over 300kWh: third tier
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

                        if "15kWh" in row_text and "120kWh" in row_text:
                            price = self._parse_price(row_text)
                            if price:
                                unit_prices["tier1_15_120"] = price
                        elif "120kWh" in row_text and "300kWh" in row_text:
                            price = self._parse_price(row_text)
                            if price:
                                unit_prices["tier2_120_300"] = price
                        elif "300kWh" in row_text and ("超" in row_text or "超過" in row_text):
                            price = self._parse_price(row_text)
                            if price:
                                unit_prices["tier3_over_300"] = price

        except Exception as e:
            logger.debug(f"Failed to extract unit prices A: {e}")

        return unit_prices

    async def _extract_unit_prices_b(self, page: Page) -> dict[str, float]:
        """Extract tiered unit prices for 従量電灯B."""
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
                        elif "300kWh" in row_text and ("超" in row_text or "超過" in row_text):
                            price = self._parse_price(row_text)
                            if price:
                                unit_prices["tier3_over_300"] = price

        except Exception as e:
            logger.debug(f"Failed to extract unit prices B: {e}")

        return unit_prices

    async def _extract_electric_delight_prices(self, page: Page) -> dict[str, float]:
        """Extract prices for Electric Delight plan."""
        unit_prices: dict[str, float] = {}

        try:
            tables = await page.query_selector_all("table")
            for table in tables:
                text = await table.inner_text()
                if "電力量料金" in text or "従量料金" in text:
                    rows = await table.query_selector_all("tr")
                    for row in rows:
                        row_text = clean_text(await row.inner_text())

                        # Electric Delight has simplified tiering
                        if "120kWh" in row_text:
                            price = self._parse_price(row_text)
                            if price:
                                if "まで" in row_text or "以下" in row_text:
                                    unit_prices["tier1_0_120"] = price
                                else:
                                    unit_prices["tier2_over_120"] = price

        except Exception as e:
            logger.debug(f"Failed to extract Electric Delight prices: {e}")

        return unit_prices

    async def _extract_fuel_adjustment(self, page: Page) -> float | None:
        """Extract fuel cost adjustment rate."""
        return None

    async def _extract_renewable_surcharge(self, page: Page) -> float | None:
        """Extract renewable energy surcharge."""
        return 1.40  # National rate for 2024
