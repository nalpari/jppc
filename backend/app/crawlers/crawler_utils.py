"""Crawler utility functions - Rate limiting, retry logic, etc."""

import asyncio
import random
from functools import wraps
from typing import Callable, TypeVar, ParamSpec

from app.utils.logger import get_logger

logger = get_logger(__name__)

P = ParamSpec("P")
T = TypeVar("T")


class RateLimiter:
    """Simple rate limiter for controlling request frequency."""

    def __init__(self, min_delay: float = 1.0, max_delay: float = 3.0):
        """Initialize rate limiter.

        Args:
            min_delay: Minimum delay between requests in seconds
            max_delay: Maximum delay between requests in seconds
        """
        self.min_delay = min_delay
        self.max_delay = max_delay
        self._last_request_time: float = 0

    async def wait(self) -> None:
        """Wait for the appropriate amount of time before next request."""
        current_time = asyncio.get_event_loop().time()
        elapsed = current_time - self._last_request_time

        # Calculate random delay
        delay = random.uniform(self.min_delay, self.max_delay)

        if elapsed < delay:
            wait_time = delay - elapsed
            logger.debug(f"Rate limiting: waiting {wait_time:.2f}s")
            await asyncio.sleep(wait_time)

        self._last_request_time = asyncio.get_event_loop().time()


def with_retry(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 30.0,
    exponential_base: float = 2.0,
    retryable_exceptions: tuple = (Exception,),
) -> Callable[[Callable[P, T]], Callable[P, T]]:
    """Decorator for retrying async functions with exponential backoff.

    Args:
        max_retries: Maximum number of retry attempts
        base_delay: Initial delay between retries in seconds
        max_delay: Maximum delay between retries in seconds
        exponential_base: Base for exponential backoff calculation
        retryable_exceptions: Tuple of exceptions that should trigger a retry
    """

    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        @wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            last_exception: Exception | None = None

            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except retryable_exceptions as e:
                    last_exception = e

                    if attempt == max_retries:
                        logger.error(
                            f"Function {func.__name__} failed after {max_retries + 1} attempts: {e}"
                        )
                        raise

                    # Calculate delay with exponential backoff and jitter
                    delay = min(
                        base_delay * (exponential_base**attempt),
                        max_delay,
                    )
                    # Add jitter (±25%)
                    delay = delay * (0.75 + random.random() * 0.5)

                    logger.warning(
                        f"Attempt {attempt + 1}/{max_retries + 1} for {func.__name__} "
                        f"failed: {e}. Retrying in {delay:.1f}s..."
                    )
                    await asyncio.sleep(delay)

            # Should never reach here, but just in case
            if last_exception:
                raise last_exception

        return wrapper

    return decorator


async def wait_for_page_load(page, timeout: int = 30000) -> None:
    """Wait for page to be fully loaded.

    Args:
        page: Playwright page object
        timeout: Maximum time to wait in milliseconds
    """
    try:
        await page.wait_for_load_state("networkidle", timeout=timeout)
    except Exception:
        # Fallback to domcontentloaded if networkidle times out
        await page.wait_for_load_state("domcontentloaded", timeout=timeout)


async def scroll_to_bottom(page, step: int = 300, delay: float = 0.1) -> None:
    """Scroll to the bottom of the page to load lazy content.

    Args:
        page: Playwright page object
        step: Pixels to scroll per step
        delay: Delay between scroll steps in seconds
    """
    prev_height = 0
    while True:
        current_height = await page.evaluate("document.body.scrollHeight")
        if current_height == prev_height:
            break
        prev_height = current_height

        await page.evaluate(f"window.scrollBy(0, {step})")
        await asyncio.sleep(delay)


def clean_text(text: str | None) -> str:
    """Clean and normalize text extracted from web pages.

    Args:
        text: Raw text to clean

    Returns:
        Cleaned text with normalized whitespace
    """
    if not text:
        return ""

    # Replace various whitespace characters with single space
    import re

    text = re.sub(r"[\s\u3000]+", " ", text)  # \u3000 is full-width space
    return text.strip()


def extract_numbers(text: str) -> list[float]:
    """Extract all numbers from a text string.

    Args:
        text: Text containing numbers

    Returns:
        List of extracted numbers as floats
    """
    import re

    # Remove commas in numbers
    text = re.sub(r"(\d),(\d)", r"\1\2", text)
    # Find all numbers (including decimals)
    matches = re.findall(r"\d+\.?\d*", text)
    return [float(m) for m in matches if m]


def parse_japanese_date(text: str) -> str | None:
    """Parse Japanese date formats to ISO format.

    Handles formats like:
    - "令和6年4月1日" -> "2024-04-01"
    - "2024年4月1日" -> "2024-04-01"
    - "R6.4.1" -> "2024-04-01"

    Args:
        text: Japanese date string

    Returns:
        ISO format date string or None if parsing fails
    """
    import re
    from datetime import datetime

    # Era name mappings
    era_to_base_year = {
        "令和": 2018,
        "平成": 1988,
        "昭和": 1925,
        "R": 2018,
        "H": 1988,
        "S": 1925,
    }

    # Try Western year format first (2024年4月1日)
    match = re.search(r"(\d{4})年(\d{1,2})月(\d{1,2})日", text)
    if match:
        year, month, day = int(match.group(1)), int(match.group(2)), int(match.group(3))
        try:
            return datetime(year, month, day).strftime("%Y-%m-%d")
        except ValueError:
            pass

    # Try Japanese era format (令和6年4月1日)
    for era, base in era_to_base_year.items():
        pattern = rf"{era}(\d{{1,2}})年(\d{{1,2}})月(\d{{1,2}})日"
        match = re.search(pattern, text)
        if match:
            year = base + int(match.group(1))
            month, day = int(match.group(2)), int(match.group(3))
            try:
                return datetime(year, month, day).strftime("%Y-%m-%d")
            except ValueError:
                pass

    # Try abbreviated format (R6.4.1)
    for era, base in era_to_base_year.items():
        pattern = rf"{era}(\d{{1,2}})\.(\d{{1,2}})\.(\d{{1,2}})"
        match = re.search(pattern, text)
        if match:
            year = base + int(match.group(1))
            month, day = int(match.group(2)), int(match.group(3))
            try:
                return datetime(year, month, day).strftime("%Y-%m-%d")
            except ValueError:
                pass

    return None
