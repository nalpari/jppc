"""Integration tests for power company crawlers."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.crawlers import (
    get_crawler,
    get_all_crawlers,
    CRAWLER_REGISTRY,
    TEPCOCrawler,
    ChubuCrawler,
    KEPCOCrawler,
    ChugokuCrawler,
)
from app.crawlers.base_crawler import PricePlanData


class TestCrawlerRegistry:
    """Tests for crawler registry functions."""

    def test_get_crawler_tepco(self):
        """Test getting TEPCO crawler."""
        crawler = get_crawler("tepco")
        assert isinstance(crawler, TEPCOCrawler)
        assert crawler.COMPANY_CODE == "tepco"

    def test_get_crawler_chubu(self):
        """Test getting Chubu crawler."""
        crawler = get_crawler("chubu")
        assert isinstance(crawler, ChubuCrawler)
        assert crawler.COMPANY_CODE == "chubu"

    def test_get_crawler_kepco(self):
        """Test getting KEPCO crawler."""
        crawler = get_crawler("kepco")
        assert isinstance(crawler, KEPCOCrawler)
        assert crawler.COMPANY_CODE == "kepco"

    def test_get_crawler_chugoku(self):
        """Test getting Chugoku crawler."""
        crawler = get_crawler("chugoku")
        assert isinstance(crawler, ChugokuCrawler)
        assert crawler.COMPANY_CODE == "chugoku"

    def test_get_crawler_case_insensitive(self):
        """Test that company code is case insensitive."""
        crawler = get_crawler("TEPCO")
        assert isinstance(crawler, TEPCOCrawler)

    def test_get_crawler_unknown(self):
        """Test that unknown company raises ValueError."""
        with pytest.raises(ValueError, match="Unknown company code"):
            get_crawler("unknown")

    def test_get_all_crawlers(self):
        """Test getting all crawlers."""
        crawlers = get_all_crawlers()
        assert len(crawlers) == 4

        codes = {c.COMPANY_CODE for c in crawlers}
        assert codes == {"tepco", "chubu", "kepco", "chugoku"}

    def test_registry_has_all_companies(self):
        """Test that registry contains all companies."""
        assert "tepco" in CRAWLER_REGISTRY
        assert "chubu" in CRAWLER_REGISTRY
        assert "kepco" in CRAWLER_REGISTRY
        assert "chugoku" in CRAWLER_REGISTRY


class TestCrawlerAttributes:
    """Tests for crawler class attributes."""

    @pytest.mark.parametrize(
        "company_code,expected_name",
        [
            ("tepco", "東京電力エナジーパートナー"),
            ("chubu", "中部電力ミライズ"),
            ("kepco", "関西電力"),
            ("chugoku", "中国電力"),
        ],
    )
    def test_company_names(self, company_code: str, expected_name: str):
        """Test that crawlers have correct company names."""
        crawler = get_crawler(company_code)
        assert crawler.COMPANY_NAME == expected_name

    @pytest.mark.parametrize(
        "company_code",
        ["tepco", "chubu", "kepco", "chugoku"],
    )
    def test_has_base_url(self, company_code: str):
        """Test that all crawlers have a base URL."""
        crawler = get_crawler(company_code)
        assert crawler.BASE_URL.startswith("https://")

    @pytest.mark.parametrize(
        "company_code",
        ["tepco", "chubu", "kepco", "chugoku"],
    )
    def test_has_price_page_urls(self, company_code: str):
        """Test that all crawlers have price page URLs."""
        crawler = get_crawler(company_code)
        urls = crawler.get_price_page_urls()
        assert len(urls) > 0
        for url in urls:
            assert url.startswith("https://")


class TestCrawlerWithMockedBrowser:
    """Tests for crawlers with mocked browser."""

    @pytest.fixture
    def mock_page(self):
        """Create a mock page object."""
        page = AsyncMock()
        page.goto = AsyncMock()
        page.close = AsyncMock()
        page.inner_text = AsyncMock(return_value="")
        page.query_selector = AsyncMock(return_value=None)
        page.query_selector_all = AsyncMock(return_value=[])
        page.wait_for_load_state = AsyncMock()
        return page

    @pytest.fixture
    def mock_context(self, mock_page):
        """Create a mock browser context."""
        context = AsyncMock()
        context.new_page = AsyncMock(return_value=mock_page)
        context.close = AsyncMock()
        context.set_default_timeout = MagicMock()
        return context

    @pytest.fixture
    def mock_browser(self, mock_context):
        """Create a mock browser."""
        browser = AsyncMock()
        browser.new_context = AsyncMock(return_value=mock_context)
        browser.close = AsyncMock()
        return browser

    @pytest.mark.asyncio
    async def test_tepco_crawler_lifecycle(self, mock_browser, mock_context, mock_page):
        """Test TEPCO crawler start/stop lifecycle."""
        with patch("app.crawlers.base_crawler.async_playwright") as mock_pw:
            mock_pw_instance = AsyncMock()
            mock_pw_instance.chromium.launch = AsyncMock(return_value=mock_browser)
            mock_pw_instance.stop = AsyncMock()
            mock_pw.return_value.start = AsyncMock(return_value=mock_pw_instance)

            crawler = TEPCOCrawler()
            await crawler.start()

            assert crawler._browser is not None
            assert crawler._context is not None

            await crawler.stop()

    @pytest.mark.asyncio
    async def test_crawler_context_manager(self, mock_browser, mock_context, mock_page):
        """Test crawler as async context manager."""
        with patch("app.crawlers.base_crawler.async_playwright") as mock_pw:
            mock_pw_instance = AsyncMock()
            mock_pw_instance.chromium.launch = AsyncMock(return_value=mock_browser)
            mock_pw_instance.stop = AsyncMock()
            mock_pw.return_value.start = AsyncMock(return_value=mock_pw_instance)

            async with TEPCOCrawler() as crawler:
                assert crawler._browser is not None
