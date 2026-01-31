"""Helper utility functions."""

from datetime import datetime
from typing import Any
from zoneinfo import ZoneInfo


def get_jst_now() -> datetime:
    """Get current datetime in Japan Standard Time (JST)."""
    return datetime.now(ZoneInfo("Asia/Tokyo"))


def utc_to_jst(dt: datetime) -> datetime:
    """Convert UTC datetime to JST."""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=ZoneInfo("UTC"))
    return dt.astimezone(ZoneInfo("Asia/Tokyo"))


def format_currency_jpy(amount: float | int) -> str:
    """Format amount as Japanese Yen.

    Args:
        amount: Amount to format.

    Returns:
        Formatted string like "¥1,234"
    """
    return f"¥{amount:,.0f}"


def safe_get(data: dict[str, Any], *keys: str, default: Any = None) -> Any:
    """Safely get nested dictionary value.

    Args:
        data: Dictionary to search.
        *keys: Sequence of keys to traverse.
        default: Default value if key not found.

    Returns:
        Value at the nested key path, or default.
    """
    result = data
    for key in keys:
        if isinstance(result, dict):
            result = result.get(key)
            if result is None:
                return default
        else:
            return default
    return result


def calculate_monthly_bill(
    usage_kwh: int,
    base_charge: float,
    price_tiers: list[dict[str, Any]] | None = None,
    unit_price: float | None = None,
    fuel_adjustment: float = 0,
    renewable_surcharge: float = 0,
) -> float:
    """Calculate estimated monthly electricity bill.

    Args:
        usage_kwh: Monthly usage in kWh.
        base_charge: Base charge in Yen.
        price_tiers: Tiered pricing structure. List of {min, max, price}.
        unit_price: Flat unit price (used if price_tiers is None).
        fuel_adjustment: Fuel adjustment per kWh.
        renewable_surcharge: Renewable energy surcharge per kWh.

    Returns:
        Estimated total monthly bill in Yen.
    """
    total = base_charge

    if price_tiers:
        remaining = usage_kwh
        for tier in sorted(price_tiers, key=lambda t: t.get("min", 0)):
            tier_min = tier.get("min", 0)
            tier_max = tier.get("max", float("inf"))
            tier_price = tier.get("price", 0)

            if remaining <= 0:
                break

            tier_usage = min(remaining, tier_max - tier_min)
            if tier_usage > 0:
                total += tier_usage * tier_price
                remaining -= tier_usage
    elif unit_price:
        total += usage_kwh * unit_price

    # Add adjustments
    total += usage_kwh * (fuel_adjustment + renewable_surcharge)

    return round(total, 2)
