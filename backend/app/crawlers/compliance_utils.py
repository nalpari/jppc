"""Compliance utilities for respectful web crawling."""

import asyncio
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

import httpx

from app.utils.logger import get_logger

logger = get_logger(__name__)


class RobotsChecker:
    """Check robots.txt compliance for URLs."""

    def __init__(self, user_agent: str = "*"):
        """Initialize robots checker.

        Args:
            user_agent: User agent to check permissions for
        """
        self.user_agent = user_agent
        self._cache: dict[str, RobotFileParser] = {}
        self._cache_ttl = 3600  # 1 hour

    async def can_fetch(self, url: str) -> bool:
        """Check if the URL can be fetched according to robots.txt.

        Args:
            url: URL to check

        Returns:
            True if fetching is allowed, False otherwise
        """
        parsed = urlparse(url)
        robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"

        try:
            parser = await self._get_parser(robots_url)
            if parser:
                return parser.can_fetch(self.user_agent, url)
        except Exception as e:
            logger.warning(f"Failed to check robots.txt for {url}: {e}")

        # Default to allowing if we can't check
        return True

    async def get_crawl_delay(self, url: str) -> float | None:
        """Get the crawl delay specified in robots.txt.

        Args:
            url: URL to check

        Returns:
            Crawl delay in seconds, or None if not specified
        """
        parsed = urlparse(url)
        robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"

        try:
            parser = await self._get_parser(robots_url)
            if parser:
                delay = parser.crawl_delay(self.user_agent)
                return float(delay) if delay else None
        except Exception as e:
            logger.warning(f"Failed to get crawl delay for {url}: {e}")

        return None

    async def _get_parser(self, robots_url: str) -> RobotFileParser | None:
        """Get or fetch robots.txt parser.

        Args:
            robots_url: URL of robots.txt file

        Returns:
            RobotFileParser instance or None
        """
        if robots_url in self._cache:
            return self._cache[robots_url]

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(robots_url)

                parser = RobotFileParser()
                parser.set_url(robots_url)

                if response.status_code == 200:
                    parser.parse(response.text.splitlines())
                else:
                    # If robots.txt doesn't exist, allow everything
                    parser.parse([])

                self._cache[robots_url] = parser
                return parser

        except Exception as e:
            logger.debug(f"Could not fetch robots.txt from {robots_url}: {e}")
            return None


# Common user agents for different purposes
USER_AGENTS = {
    "default": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "bot": "JPPC-Crawler/1.0 (+https://github.com/jppc)",
    "mobile": (
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) "
        "AppleWebKit/605.1.15 (KHTML, like Gecko) "
        "Version/17.0 Mobile/15E148 Safari/604.1"
    ),
}


def get_user_agent(agent_type: str = "default") -> str:
    """Get a user agent string.

    Args:
        agent_type: Type of user agent (default, bot, mobile)

    Returns:
        User agent string
    """
    return USER_AGENTS.get(agent_type, USER_AGENTS["default"])


async def respectful_request(
    url: str,
    method: str = "GET",
    headers: dict | None = None,
    min_delay: float = 1.0,
    check_robots: bool = True,
    **kwargs,
) -> httpx.Response:
    """Make a respectful HTTP request with rate limiting and robots.txt checking.

    Args:
        url: URL to request
        method: HTTP method
        headers: Additional headers
        min_delay: Minimum delay before request
        check_robots: Whether to check robots.txt
        **kwargs: Additional arguments for httpx

    Returns:
        HTTP response

    Raises:
        PermissionError: If robots.txt disallows the request
    """
    # Check robots.txt
    if check_robots:
        checker = RobotsChecker()
        if not await checker.can_fetch(url):
            raise PermissionError(f"robots.txt disallows fetching: {url}")

        # Respect crawl delay from robots.txt
        delay = await checker.get_crawl_delay(url)
        if delay and delay > min_delay:
            min_delay = delay

    # Apply rate limiting
    await asyncio.sleep(min_delay)

    # Make request
    default_headers = {
        "User-Agent": get_user_agent("default"),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "ja,en-US;q=0.9,en;q=0.8",
    }
    if headers:
        default_headers.update(headers)

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.request(method, url, headers=default_headers, **kwargs)
        return response
