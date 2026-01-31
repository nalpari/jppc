"""Tests for base crawler functionality."""

import pytest
from datetime import datetime

from app.crawlers.base_crawler import BaseCrawler, PricePlanData, CrawlResult


class TestPricePlanData:
    """Tests for PricePlanData dataclass."""

    def test_creation_minimal(self):
        """Test creating PricePlanData with minimal fields."""
        plan = PricePlanData(plan_name="Test Plan")

        assert plan.plan_name == "Test Plan"
        assert plan.plan_code is None
        assert plan.base_charge is None
        assert plan.unit_prices == {}

    def test_creation_full(self):
        """Test creating PricePlanData with all fields."""
        plan = PricePlanData(
            plan_name="従量電灯B",
            plan_code="tepco_metered_b",
            contract_type="従量電灯",
            base_charge=885.72,
            unit_prices={
                "tier1_0_120": 29.80,
                "tier2_120_300": 36.40,
                "tier3_over_300": 40.49,
            },
            minimum_charge=None,
            fuel_adjustment=-3.50,
            renewable_surcharge=1.40,
            effective_date=datetime(2024, 4, 1),
            source_url="https://www.tepco.co.jp/",
            raw_data={"crawled_at": "2024-01-01T00:00:00"},
        )

        assert plan.plan_name == "従量電灯B"
        assert plan.plan_code == "tepco_metered_b"
        assert plan.base_charge == 885.72
        assert len(plan.unit_prices) == 3
        assert plan.unit_prices["tier1_0_120"] == 29.80


class TestCrawlResult:
    """Tests for CrawlResult dataclass."""

    def test_successful_result(self):
        """Test creating a successful crawl result."""
        plan = PricePlanData(plan_name="Test Plan")
        result = CrawlResult(
            success=True,
            company_code="tepco",
            plans=[plan],
            duration_seconds=5.5,
            pages_crawled=3,
        )

        assert result.success is True
        assert result.company_code == "tepco"
        assert len(result.plans) == 1
        assert result.error_message is None
        assert result.duration_seconds == 5.5
        assert result.pages_crawled == 3

    def test_failed_result(self):
        """Test creating a failed crawl result."""
        result = CrawlResult(
            success=False,
            company_code="tepco",
            error_message="Connection timeout",
            duration_seconds=30.0,
        )

        assert result.success is False
        assert result.error_message == "Connection timeout"
        assert len(result.plans) == 0


class TestBaseCrawler:
    """Tests for BaseCrawler abstract class."""

    def test_parse_price_yen(self):
        """Test parsing Japanese yen prices."""

        class DummyCrawler(BaseCrawler):
            COMPANY_CODE = "test"
            COMPANY_NAME = "Test"
            BASE_URL = "https://test.com"

            async def _crawl_prices(self):
                return [], 0

            def get_price_page_urls(self):
                return []

        crawler = DummyCrawler()

        assert crawler._parse_price("1,234円") == 1234.0
        assert crawler._parse_price("29.80円/kWh") == 29.80
        assert crawler._parse_price("¥1,234") == 1234.0
        assert crawler._parse_price("885.72円") == 885.72
        assert crawler._parse_price(None) is None
        assert crawler._parse_price("") is None

    def test_company_attributes(self):
        """Test that subclasses must define company attributes."""

        class DummyCrawler(BaseCrawler):
            COMPANY_CODE = "dummy"
            COMPANY_NAME = "Dummy Electric"
            BASE_URL = "https://dummy.co.jp"

            async def _crawl_prices(self):
                return [], 0

            def get_price_page_urls(self):
                return ["https://dummy.co.jp/prices"]

        crawler = DummyCrawler()

        assert crawler.COMPANY_CODE == "dummy"
        assert crawler.COMPANY_NAME == "Dummy Electric"
        assert crawler.BASE_URL == "https://dummy.co.jp"
        assert len(crawler.get_price_page_urls()) == 1
