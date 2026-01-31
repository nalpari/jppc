"""Power company crawlers package.

This package contains crawlers for Japanese power companies:
- TEPCO (Tokyo Electric Power Company) - 東京電力
- Chubu Electric - 中部電力
- KEPCO (Kansai Electric Power Company) - 関西電力
- Chugoku Electric - 中国電力
"""

from app.crawlers.base_crawler import BaseCrawler, PricePlanData, CrawlResult
from app.crawlers.tepco_crawler import TEPCOCrawler
from app.crawlers.chubu_crawler import ChubuCrawler
from app.crawlers.kepco_crawler import KEPCOCrawler
from app.crawlers.chugoku_crawler import ChugokuCrawler

# Crawler registry - maps company code to crawler class
CRAWLER_REGISTRY: dict[str, type[BaseCrawler]] = {
    "tepco": TEPCOCrawler,
    "chubu": ChubuCrawler,
    "kepco": KEPCOCrawler,
    "chugoku": ChugokuCrawler,
}


def get_crawler(company_code: str, **kwargs) -> BaseCrawler:
    """Get a crawler instance for the specified company.

    Args:
        company_code: Company code (tepco, chubu, kepco, chugoku)
        **kwargs: Additional arguments passed to crawler constructor

    Returns:
        Crawler instance

    Raises:
        ValueError: If company_code is not recognized
    """
    crawler_class = CRAWLER_REGISTRY.get(company_code.lower())
    if not crawler_class:
        available = ", ".join(CRAWLER_REGISTRY.keys())
        raise ValueError(
            f"Unknown company code: {company_code}. Available: {available}"
        )
    return crawler_class(**kwargs)


def get_all_crawlers(**kwargs) -> list[BaseCrawler]:
    """Get crawler instances for all companies.

    Args:
        **kwargs: Additional arguments passed to crawler constructors

    Returns:
        List of crawler instances
    """
    return [crawler_class(**kwargs) for crawler_class in CRAWLER_REGISTRY.values()]


__all__ = [
    # Base classes
    "BaseCrawler",
    "PricePlanData",
    "CrawlResult",
    # Crawler implementations
    "TEPCOCrawler",
    "ChubuCrawler",
    "KEPCOCrawler",
    "ChugokuCrawler",
    # Registry and factory
    "CRAWLER_REGISTRY",
    "get_crawler",
    "get_all_crawlers",
]
