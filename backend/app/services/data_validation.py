"""Data validation and change detection for crawled price data."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from app.crawlers import PricePlanData
from app.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class ValidationError:
    """Represents a validation error."""

    field: str
    message: str
    severity: str = "error"  # error, warning


@dataclass
class ValidationResult:
    """Result of data validation."""

    is_valid: bool
    errors: list[ValidationError] = field(default_factory=list)
    warnings: list[ValidationError] = field(default_factory=list)

    def add_error(self, field: str, message: str) -> None:
        """Add a validation error."""
        self.errors.append(ValidationError(field, message, "error"))
        self.is_valid = False

    def add_warning(self, field: str, message: str) -> None:
        """Add a validation warning."""
        self.warnings.append(ValidationError(field, message, "warning"))


@dataclass
class PriceChange:
    """Represents a price change detection."""

    plan_code: str
    plan_name: str
    field: str
    old_value: Any
    new_value: Any
    change_percentage: float | None = None
    detected_at: datetime = field(default_factory=datetime.utcnow)


class PriceDataValidator:
    """Validates crawled price data."""

    # Reasonable price ranges for Japanese electricity (in yen)
    MIN_BASE_CHARGE = 100  # Minimum base charge
    MAX_BASE_CHARGE = 10000  # Maximum base charge for residential
    MIN_UNIT_PRICE = 10  # Minimum per kWh price
    MAX_UNIT_PRICE = 100  # Maximum per kWh price
    MIN_RENEWABLE_SURCHARGE = 0
    MAX_RENEWABLE_SURCHARGE = 10  # Current is around 1.4 yen/kWh

    def validate(self, plan: PricePlanData) -> ValidationResult:
        """Validate a price plan.

        Args:
            plan: Price plan data to validate

        Returns:
            ValidationResult with any errors/warnings
        """
        result = ValidationResult(is_valid=True)

        # Required fields
        if not plan.plan_name:
            result.add_error("plan_name", "Plan name is required")

        if not plan.plan_code:
            result.add_error("plan_code", "Plan code is required")

        # Validate base charge
        if plan.base_charge is not None:
            if plan.base_charge < self.MIN_BASE_CHARGE:
                result.add_warning(
                    "base_charge",
                    f"Base charge {plan.base_charge} is unusually low",
                )
            elif plan.base_charge > self.MAX_BASE_CHARGE:
                result.add_error(
                    "base_charge",
                    f"Base charge {plan.base_charge} exceeds maximum {self.MAX_BASE_CHARGE}",
                )

        # Validate minimum charge (for plans without base charge)
        if plan.minimum_charge is not None:
            if plan.minimum_charge < 0:
                result.add_error(
                    "minimum_charge",
                    f"Minimum charge cannot be negative: {plan.minimum_charge}",
                )

        # Validate unit prices
        if plan.unit_prices:
            for tier, price in plan.unit_prices.items():
                if price < self.MIN_UNIT_PRICE:
                    result.add_warning(
                        f"unit_prices.{tier}",
                        f"Unit price {price} is unusually low",
                    )
                elif price > self.MAX_UNIT_PRICE:
                    result.add_error(
                        f"unit_prices.{tier}",
                        f"Unit price {price} exceeds maximum {self.MAX_UNIT_PRICE}",
                    )

            # Check tier ordering (higher tiers should have higher prices generally)
            self._validate_tier_ordering(plan.unit_prices, result)

        # Validate renewable surcharge
        if plan.renewable_surcharge is not None:
            if plan.renewable_surcharge < self.MIN_RENEWABLE_SURCHARGE:
                result.add_error(
                    "renewable_surcharge",
                    f"Renewable surcharge cannot be negative",
                )
            elif plan.renewable_surcharge > self.MAX_RENEWABLE_SURCHARGE:
                result.add_warning(
                    "renewable_surcharge",
                    f"Renewable surcharge {plan.renewable_surcharge} is unusually high",
                )

        return result

    def _validate_tier_ordering(
        self, unit_prices: dict[str, float], result: ValidationResult
    ) -> None:
        """Validate that tier prices are reasonably ordered."""
        # Extract tier numbers and prices
        tier_prices: list[tuple[int, float]] = []
        for tier, price in unit_prices.items():
            if "tier1" in tier:
                tier_prices.append((1, price))
            elif "tier2" in tier:
                tier_prices.append((2, price))
            elif "tier3" in tier:
                tier_prices.append((3, price))

        # Sort by tier number
        tier_prices.sort(key=lambda x: x[0])

        # Check ordering (later tiers should generally have higher or equal prices)
        for i in range(1, len(tier_prices)):
            prev_tier, prev_price = tier_prices[i - 1]
            curr_tier, curr_price = tier_prices[i]
            if curr_price < prev_price * 0.8:  # Allow some flexibility
                result.add_warning(
                    "unit_prices",
                    f"Tier {curr_tier} price ({curr_price}) is significantly lower than tier {prev_tier} ({prev_price})",
                )


class PriceChangeDetector:
    """Detects changes in price data."""

    # Threshold for significant price change (percentage)
    SIGNIFICANT_CHANGE_THRESHOLD = 5.0

    def detect_changes(
        self,
        old_plan: dict[str, Any],
        new_plan: PricePlanData,
    ) -> list[PriceChange]:
        """Detect changes between old and new price data.

        Args:
            old_plan: Existing plan data from database
            new_plan: Newly crawled plan data

        Returns:
            List of detected changes
        """
        changes: list[PriceChange] = []

        # Compare base charge
        old_base = old_plan.get("base_charge")
        new_base = new_plan.base_charge
        if old_base != new_base and old_base is not None and new_base is not None:
            change_pct = ((new_base - old_base) / old_base) * 100 if old_base else None
            changes.append(
                PriceChange(
                    plan_code=new_plan.plan_code or "",
                    plan_name=new_plan.plan_name,
                    field="base_charge",
                    old_value=old_base,
                    new_value=new_base,
                    change_percentage=change_pct,
                )
            )

        # Compare minimum charge
        old_min = old_plan.get("minimum_charge")
        new_min = new_plan.minimum_charge
        if old_min != new_min and old_min is not None and new_min is not None:
            change_pct = ((new_min - old_min) / old_min) * 100 if old_min else None
            changes.append(
                PriceChange(
                    plan_code=new_plan.plan_code or "",
                    plan_name=new_plan.plan_name,
                    field="minimum_charge",
                    old_value=old_min,
                    new_value=new_min,
                    change_percentage=change_pct,
                )
            )

        # Compare unit prices
        old_prices = old_plan.get("unit_prices", {})
        new_prices = new_plan.unit_prices

        all_tiers = set(old_prices.keys()) | set(new_prices.keys())
        for tier in all_tiers:
            old_price = old_prices.get(tier)
            new_price = new_prices.get(tier)

            if old_price != new_price:
                change_pct = None
                if old_price and new_price:
                    change_pct = ((new_price - old_price) / old_price) * 100

                changes.append(
                    PriceChange(
                        plan_code=new_plan.plan_code or "",
                        plan_name=new_plan.plan_name,
                        field=f"unit_prices.{tier}",
                        old_value=old_price,
                        new_value=new_price,
                        change_percentage=change_pct,
                    )
                )

        # Compare fuel adjustment
        old_fuel = old_plan.get("fuel_adjustment")
        new_fuel = new_plan.fuel_adjustment
        if old_fuel != new_fuel:
            changes.append(
                PriceChange(
                    plan_code=new_plan.plan_code or "",
                    plan_name=new_plan.plan_name,
                    field="fuel_adjustment",
                    old_value=old_fuel,
                    new_value=new_fuel,
                )
            )

        # Compare renewable surcharge
        old_renewable = old_plan.get("renewable_surcharge")
        new_renewable = new_plan.renewable_surcharge
        if old_renewable != new_renewable:
            changes.append(
                PriceChange(
                    plan_code=new_plan.plan_code or "",
                    plan_name=new_plan.plan_name,
                    field="renewable_surcharge",
                    old_value=old_renewable,
                    new_value=new_renewable,
                )
            )

        return changes

    def filter_significant_changes(
        self,
        changes: list[PriceChange],
    ) -> list[PriceChange]:
        """Filter to only significant price changes.

        Args:
            changes: List of all detected changes

        Returns:
            List of significant changes only
        """
        return [
            change
            for change in changes
            if change.change_percentage is not None
            and abs(change.change_percentage) >= self.SIGNIFICANT_CHANGE_THRESHOLD
        ]
