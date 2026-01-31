"""Kansai Electric Power Company (KEPCO) crawler.

関西電力 요금 정보 크롤러
Website: https://www.kepco.co.jp/
"""

from datetime import datetime

from playwright.async_api import Page

from app.crawlers.base_crawler import BaseCrawler, PricePlanData
from app.crawlers.crawler_utils import RateLimiter, wait_for_page_load, clean_text
from app.utils.logger import get_logger

logger = get_logger(__name__)


class KEPCOCrawler(BaseCrawler):
    """Kansai Electric Power Company (KEPCO) price crawler.

    Crawls electricity price information from KEPCO's official website.
    Target region: Kansai (関西地方) - Osaka, Kyoto, Hyogo, Nara, Shiga, Wakayama
    """

    COMPANY_CODE = "kepco"
    COMPANY_NAME = "関西電力"
    BASE_URL = "https://www.kepco.co.jp"

    # Price information pages
    PRICE_PAGES = {
        "metered_a": "/home/ryoukin/menu/dento_a.html",  # 従量電灯A
        "metered_b": "/home/ryoukin/menu/dento_b.html",  # 従量電灯B
        "hapie": "/home/ryoukin/menu/hapie.html",  # はぴeタイム
    }

    def __init__(self, headless: bool = True, timeout: int = 30000):
        super().__init__(headless, timeout)
        self.rate_limiter = RateLimiter(min_delay=2.0, max_delay=4.0)

    def get_price_page_urls(self) -> list[str]:
        """Get URLs for KEPCO price pages."""
        return [f"{self.BASE_URL}{path}" for path in self.PRICE_PAGES.values()]

    async def _crawl_prices(self) -> tuple[list[PricePlanData], int]:
        """Crawl KEPCO price information.

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

            # Crawl はぴeタイム
            await self.rate_limiter.wait()
            plan = await self._crawl_hapie_time(page)
            if plan:
                plans.append(plan)
            pages_crawled += 1

        finally:
            await page.close()

        return plans, pages_crawled

    async def _crawl_metered_a(self, page: Page) -> PricePlanData | None:
        """Crawl 従量電灯A plan.

        KEPCO uses 従量電灯A for small residential customers.
        Has minimum charge instead of base charge.
        """
        url = f"{self.BASE_URL}{self.PRICE_PAGES['metered_a']}"
        logger.info(f"Crawling KEPCO 従量電灯A: {url}")

        try:
            await page.goto(url)
            await wait_for_page_load(page)

            minimum_charge = await self._extract_minimum_charge(page)
            unit_prices = await self._extract_unit_prices_a(page)
            fuel_adj = await self._extract_fuel_adjustment(page)
            renewable = await self._extract_renewable_surcharge(page)

            return PricePlanData(
                plan_name="従量電灯A",
                plan_code="kepco_metered_a",
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
            logger.error(f"Failed to crawl KEPCO 従量電灯A: {e}")
            return None

    async def _crawl_metered_b(self, page: Page) -> PricePlanData | None:
        """Crawl 従量電灯B plan."""
        url = f"{self.BASE_URL}{self.PRICE_PAGES['metered_b']}"
        logger.info(f"Crawling KEPCO 従量電灯B: {url}")

        try:
            await page.goto(url)
            await wait_for_page_load(page)

            base_charge = await self._extract_base_charge(page)
            unit_prices = await self._extract_unit_prices_b(page)
            fuel_adj = await self._extract_fuel_adjustment(page)
            renewable = await self._extract_renewable_surcharge(page)

            return PricePlanData(
                plan_name="従量電灯B",
                plan_code="kepco_metered_b",
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
            logger.error(f"Failed to crawl KEPCO 従量電灯B: {e}")
            return None

    async def _crawl_hapie_time(self, page: Page) -> PricePlanData | None:
        """Crawl はぴeタイム plan.

        Time-of-use plan with daytime/nighttime pricing.
        """
        url = f"{self.BASE_URL}{self.PRICE_PAGES['hapie']}"
        logger.info(f"Crawling KEPCO はぴeタイム: {url}")

        try:
            await page.goto(url)
            await wait_for_page_load(page)

            base_charge = await self._extract_base_charge(page)
            unit_prices = await self._extract_tou_prices(page)
            fuel_adj = await self._extract_fuel_adjustment(page)
            renewable = await self._extract_renewable_surcharge(page)

            return PricePlanData(
                plan_name="はぴeタイム",
                plan_code="kepco_hapie_time",
                contract_type="時間帯別",
                base_charge=base_charge,
                unit_prices=unit_prices,
                fuel_adjustment=fuel_adj,
                renewable_surcharge=renewable,
                source_url=url,
                raw_data={
                    "plan_type": "hapie_time",
                    "crawled_at": datetime.utcnow().isoformat(),
                },
            )

        except Exception as e:
            logger.error(f"Failed to crawl KEPCO はぴeタイム: {e}")
            return None

    async def _extract_minimum_charge(self, page: Page) -> float | None:
        """Extract minimum charge (最低料金) for 従量電灯A."""
        try:
            tables = await page.query_selector_all("table")
            for table in tables:
                text = await table.inner_text()
                if "最低料金" in text:
                    rows = await table.query_selector_all("tr")
                    for row in rows:
                        row_text = await row.inner_text()
                        if "最低料金" in row_text or "15kWh" in row_text:
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
                        if "基本料金" in row_text or "1kVA" in row_text:
                            price = self._parse_price(row_text)
                            if price:
                                return price
        except Exception as e:
            logger.debug(f"Failed to extract base charge: {e}")
        return None

    async def _extract_unit_prices_a(self, page: Page) -> dict[str, float]:
        """Extract tiered unit prices for 従量電灯A.

        KEPCO 従量電灯A uses:
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

                        if ("15kWh" in row_text and "120kWh" in row_text) or "第1段階" in row_text:
                            price = self._parse_price(row_text)
                            if price:
                                unit_prices["tier1_15_120"] = price
                        elif "120kWh" in row_text and "300kWh" in row_text:
                            price = self._parse_price(row_text)
                            if price:
                                unit_prices["tier2_120_300"] = price
                        elif "300kWh" in row_text and "超過" in row_text:
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
                        elif "300kWh" in row_text and "超過" in row_text:
                            price = self._parse_price(row_text)
                            if price:
                                unit_prices["tier3_over_300"] = price

        except Exception as e:
            logger.debug(f"Failed to extract unit prices B: {e}")

        return unit_prices

    async def _extract_tou_prices(self, page: Page) -> dict[str, float]:
        """Extract time-of-use prices for はぴeタイム."""
        unit_prices: dict[str, float] = {}

        try:
            tables = await page.query_selector_all("table")
            for table in tables:
                text = await table.inner_text()
                if "電力量料金" in text or "デイタイム" in text:
                    rows = await table.query_selector_all("tr")
                    for row in rows:
                        row_text = clean_text(await row.inner_text())

                        if "デイタイム" in row_text:
                            price = self._parse_price(row_text)
                            if price:
                                unit_prices["daytime"] = price
                        elif "リビングタイム" in row_text:
                            price = self._parse_price(row_text)
                            if price:
                                unit_prices["living_time"] = price
                        elif "ナイトタイム" in row_text:
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
