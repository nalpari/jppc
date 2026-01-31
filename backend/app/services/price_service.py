"""Price service for managing price data and comparisons."""

from datetime import datetime, timedelta
from typing import Any

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Company, PricePlan, PriceHistory
from app.utils.logger import get_logger

logger = get_logger(__name__)


class PriceService:
    """Service for price data operations."""

    async def get_current_prices(
        self,
        db: AsyncSession,
        company_id: int | None = None,
    ) -> list[dict[str, Any]]:
        """Get current prices for all or specific company.

        Args:
            db: Database session
            company_id: Optional company ID filter

        Returns:
            List of price plan dictionaries
        """
        query = (
            select(PricePlan)
            .options(selectinload(PricePlan.company))
            .where(PricePlan.is_current == True)
        )

        if company_id:
            query = query.where(PricePlan.company_id == company_id)

        result = await db.execute(query)
        plans = result.scalars().all()

        return [
            {
                "id": plan.id,
                "company_id": plan.company_id,
                "company_name": plan.company.name if plan.company else None,
                "company_code": plan.company.code if plan.company else None,
                "plan_name": plan.plan_name,
                "plan_code": plan.plan_code,
                "contract_type": plan.contract_type,
                "base_charge": plan.base_charge,
                "minimum_charge": plan.minimum_charge,
                "unit_prices": plan.unit_prices,
                "fuel_adjustment": plan.fuel_adjustment,
                "renewable_surcharge": plan.renewable_surcharge,
                "effective_date": plan.effective_date,
                "updated_at": plan.updated_at,
            }
            for plan in plans
        ]

    async def get_price_history(
        self,
        db: AsyncSession,
        plan_id: int | None = None,
        company_id: int | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """Get price change history.

        Args:
            db: Database session
            plan_id: Optional plan ID filter
            company_id: Optional company ID filter
            start_date: Optional start date filter
            end_date: Optional end date filter
            limit: Maximum records to return

        Returns:
            List of price history records
        """
        query = (
            select(PriceHistory)
            .options(selectinload(PriceHistory.price_plan))
            .order_by(PriceHistory.recorded_at.desc())
            .limit(limit)
        )

        if plan_id:
            query = query.where(PriceHistory.price_plan_id == plan_id)

        if company_id:
            query = query.join(PricePlan).where(PricePlan.company_id == company_id)

        if start_date:
            query = query.where(PriceHistory.recorded_at >= start_date)

        if end_date:
            query = query.where(PriceHistory.recorded_at <= end_date)

        result = await db.execute(query)
        histories = result.scalars().all()

        return [
            {
                "id": h.id,
                "price_plan_id": h.price_plan_id,
                "plan_name": h.price_plan.plan_name if h.price_plan else None,
                "base_charge": h.base_charge,
                "minimum_charge": h.minimum_charge,
                "unit_prices": h.unit_prices,
                "fuel_adjustment": h.fuel_adjustment,
                "renewable_surcharge": h.renewable_surcharge,
                "effective_date": h.effective_date,
                "recorded_at": h.recorded_at,
                "change_type": h.change_type,
            }
            for h in histories
        ]

    async def compare_prices(
        self,
        db: AsyncSession,
        company_ids: list[int] | None = None,
        plan_type: str | None = None,
        usage_kwh: int = 300,
    ) -> list[dict[str, Any]]:
        """Compare prices across companies.

        Args:
            db: Database session
            company_ids: List of company IDs to compare
            plan_type: Optional plan type filter (e.g., "従量電灯")
            usage_kwh: Monthly usage in kWh for calculation

        Returns:
            List of comparison results
        """
        query = (
            select(PricePlan)
            .options(selectinload(PricePlan.company))
            .where(PricePlan.is_current == True)
        )

        if company_ids:
            query = query.where(PricePlan.company_id.in_(company_ids))

        if plan_type:
            query = query.where(PricePlan.contract_type == plan_type)

        result = await db.execute(query)
        plans = result.scalars().all()

        comparisons = []
        for plan in plans:
            estimated = self._calculate_monthly_cost(plan, usage_kwh)
            comparisons.append(
                {
                    "company_id": plan.company_id,
                    "company_name": plan.company.name if plan.company else None,
                    "company_code": plan.company.code if plan.company else None,
                    "plan_id": plan.id,
                    "plan_name": plan.plan_name,
                    "plan_code": plan.plan_code,
                    "contract_type": plan.contract_type,
                    "base_charge": plan.base_charge,
                    "minimum_charge": plan.minimum_charge,
                    "unit_prices": plan.unit_prices,
                    "usage_kwh": usage_kwh,
                    "estimated_monthly_cost": estimated,
                    "fuel_adjustment": plan.fuel_adjustment,
                    "renewable_surcharge": plan.renewable_surcharge,
                }
            )

        # Sort by estimated cost
        comparisons.sort(key=lambda x: x["estimated_monthly_cost"] or float("inf"))

        return comparisons

    def _calculate_monthly_cost(
        self,
        plan: PricePlan,
        usage_kwh: int,
    ) -> float | None:
        """Calculate estimated monthly cost.

        Args:
            plan: Price plan
            usage_kwh: Monthly usage in kWh

        Returns:
            Estimated monthly cost in yen
        """
        if not plan.unit_prices:
            return None

        total = 0.0

        # Add base charge or minimum charge
        if plan.base_charge:
            total += plan.base_charge
        elif plan.minimum_charge:
            total += plan.minimum_charge

        # Calculate tiered usage charges
        remaining_kwh = usage_kwh
        unit_prices = plan.unit_prices

        # Standard 3-tier pricing
        if "tier1_0_120" in unit_prices:
            tier1_kwh = min(remaining_kwh, 120)
            total += tier1_kwh * unit_prices["tier1_0_120"]
            remaining_kwh -= tier1_kwh

            if remaining_kwh > 0 and "tier2_120_300" in unit_prices:
                tier2_kwh = min(remaining_kwh, 180)  # 300 - 120
                total += tier2_kwh * unit_prices["tier2_120_300"]
                remaining_kwh -= tier2_kwh

                if remaining_kwh > 0 and "tier3_over_300" in unit_prices:
                    total += remaining_kwh * unit_prices["tier3_over_300"]

        # KEPCO-style with minimum charge included
        elif "tier1_15_120" in unit_prices:
            # First 15kWh included in minimum
            remaining_kwh = max(0, usage_kwh - 15)

            tier1_kwh = min(remaining_kwh, 105)  # 120 - 15
            total += tier1_kwh * unit_prices["tier1_15_120"]
            remaining_kwh -= tier1_kwh

            if remaining_kwh > 0 and "tier2_120_300" in unit_prices:
                tier2_kwh = min(remaining_kwh, 180)
                total += tier2_kwh * unit_prices["tier2_120_300"]
                remaining_kwh -= tier2_kwh

                if remaining_kwh > 0 and "tier3_over_300" in unit_prices:
                    total += remaining_kwh * unit_prices["tier3_over_300"]

        # Time-of-use pricing (simplified)
        elif "daytime" in unit_prices and "nighttime" in unit_prices:
            # Assume 60% daytime, 40% nighttime
            daytime_kwh = usage_kwh * 0.6
            nighttime_kwh = usage_kwh * 0.4
            total += daytime_kwh * unit_prices["daytime"]
            total += nighttime_kwh * unit_prices["nighttime"]

        # Add fuel adjustment
        if plan.fuel_adjustment:
            total += usage_kwh * plan.fuel_adjustment

        # Add renewable surcharge
        if plan.renewable_surcharge:
            total += usage_kwh * plan.renewable_surcharge

        return round(total, 2)

    async def get_price_trends(
        self,
        db: AsyncSession,
        company_id: int | None = None,
        months: int = 12,
    ) -> list[dict[str, Any]]:
        """Get price trends over time.

        Args:
            db: Database session
            company_id: Optional company filter
            months: Number of months to look back

        Returns:
            Monthly price trend data
        """
        start_date = datetime.utcnow() - timedelta(days=months * 30)

        query = (
            select(
                func.date_trunc("month", PriceHistory.recorded_at).label("month"),
                func.avg(PriceHistory.base_charge).label("avg_base_charge"),
                func.count().label("change_count"),
            )
            .where(PriceHistory.recorded_at >= start_date)
            .group_by(func.date_trunc("month", PriceHistory.recorded_at))
            .order_by(func.date_trunc("month", PriceHistory.recorded_at))
        )

        if company_id:
            query = query.join(PricePlan).where(PricePlan.company_id == company_id)

        result = await db.execute(query)
        rows = result.all()

        return [
            {
                "month": row.month.isoformat() if row.month else None,
                "avg_base_charge": float(row.avg_base_charge) if row.avg_base_charge else None,
                "change_count": row.change_count,
            }
            for row in rows
        ]


# Global service instance
price_service = PriceService()
