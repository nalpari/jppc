"""Prices API endpoints."""

from decimal import Decimal

from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import select, func

from app.api.deps import DbSession
from app.models import Company, PricePlan, PriceHistory
from app.schemas import (
    PricePlanCreate,
    PricePlanUpdate,
    PricePlanResponse,
    PricePlanListResponse,
    PriceHistoryResponse,
    PriceCompareRequest,
    PriceCompareResponse,
    PriceCompareItem,
)
from app.utils.helpers import calculate_monthly_bill

router = APIRouter()


@router.get("", response_model=PricePlanListResponse)
async def list_prices(
    db: DbSession,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    company_id: int | None = None,
    plan_type: str | None = None,
    is_current: bool | None = True,
):
    """요금제 목록 조회."""
    query = select(PricePlan)

    if company_id is not None:
        query = query.where(PricePlan.company_id == company_id)
    if plan_type is not None:
        query = query.where(PricePlan.plan_type == plan_type)
    if is_current is not None:
        query = query.where(PricePlan.is_current == is_current)

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query) or 0

    # Get paginated results with company join
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    plans = result.scalars().all()

    # Enrich with company names
    items = []
    for plan in plans:
        company = await db.scalar(select(Company).where(Company.id == plan.company_id))
        plan_dict = {
            **plan.__dict__,
            "company_name": company.name_en if company else None,
        }
        items.append(PricePlanResponse.model_validate(plan_dict))

    return PricePlanListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{price_id}", response_model=PricePlanResponse)
async def get_price(db: DbSession, price_id: int):
    """요금제 상세 조회."""
    query = select(PricePlan).where(PricePlan.id == price_id)
    result = await db.execute(query)
    plan = result.scalar_one_or_none()

    if not plan:
        raise HTTPException(status_code=404, detail="Price plan not found")

    company = await db.scalar(select(Company).where(Company.id == plan.company_id))
    plan_dict = {
        **plan.__dict__,
        "company_name": company.name_en if company else None,
    }
    return PricePlanResponse.model_validate(plan_dict)


@router.post("", response_model=PricePlanResponse, status_code=201)
async def create_price(db: DbSession, data: PricePlanCreate):
    """요금제 등록."""
    # Check company exists
    company = await db.scalar(select(Company).where(Company.id == data.company_id))
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    plan = PricePlan(
        company_id=data.company_id,
        plan_code=data.plan_code,
        plan_name_ja=data.plan_name_ja,
        plan_name_en=data.plan_name_en,
        plan_type=data.plan_type,
        contract_type=data.contract_type,
        base_charge=data.base_charge,
        unit_price=data.unit_price,
        price_tiers=data.price_tiers,
        time_of_use=data.time_of_use,
        fuel_adjustment=data.fuel_adjustment,
        renewable_surcharge=data.renewable_surcharge,
        effective_date=data.effective_date,
        source_url=data.source_url,
        notes=data.notes,
    )
    db.add(plan)
    await db.flush()
    await db.refresh(plan)

    # Create initial history record
    history = PriceHistory(
        price_plan_id=plan.id,
        base_charge=plan.base_charge,
        unit_price=plan.unit_price,
        price_tiers=plan.price_tiers,
        fuel_adjustment=plan.fuel_adjustment,
        renewable_surcharge=plan.renewable_surcharge,
        change_type="created",
    )
    db.add(history)

    plan_dict = {**plan.__dict__, "company_name": company.name_en}
    return PricePlanResponse.model_validate(plan_dict)


@router.patch("/{price_id}", response_model=PricePlanResponse)
async def update_price(db: DbSession, price_id: int, data: PricePlanUpdate):
    """요금제 정보 수정."""
    query = select(PricePlan).where(PricePlan.id == price_id)
    result = await db.execute(query)
    plan = result.scalar_one_or_none()

    if not plan:
        raise HTTPException(status_code=404, detail="Price plan not found")

    update_data = data.model_dump(exclude_unset=True)

    # Track price changes
    price_fields = {"base_charge", "unit_price", "price_tiers", "fuel_adjustment", "renewable_surcharge"}
    price_changed = any(
        field in update_data and getattr(plan, field) != update_data[field]
        for field in price_fields
    )

    for field, value in update_data.items():
        setattr(plan, field, value)

    await db.flush()
    await db.refresh(plan)

    # Record history if price changed
    if price_changed:
        history = PriceHistory(
            price_plan_id=plan.id,
            base_charge=plan.base_charge,
            unit_price=plan.unit_price,
            price_tiers=plan.price_tiers,
            fuel_adjustment=plan.fuel_adjustment,
            renewable_surcharge=plan.renewable_surcharge,
            change_type="price_change",
            change_details={"updated_fields": list(update_data.keys())},
        )
        db.add(history)

    company = await db.scalar(select(Company).where(Company.id == plan.company_id))
    plan_dict = {**plan.__dict__, "company_name": company.name_en if company else None}
    return PricePlanResponse.model_validate(plan_dict)


@router.delete("/{price_id}", status_code=204)
async def delete_price(db: DbSession, price_id: int):
    """요금제 삭제."""
    query = select(PricePlan).where(PricePlan.id == price_id)
    result = await db.execute(query)
    plan = result.scalar_one_or_none()

    if not plan:
        raise HTTPException(status_code=404, detail="Price plan not found")

    await db.delete(plan)


@router.get("/{price_id}/history", response_model=list[PriceHistoryResponse])
async def get_price_history(
    db: DbSession,
    price_id: int,
    limit: int = Query(50, ge=1, le=200),
):
    """요금 변동 이력 조회."""
    # Check plan exists
    plan = await db.scalar(select(PricePlan).where(PricePlan.id == price_id))
    if not plan:
        raise HTTPException(status_code=404, detail="Price plan not found")

    query = (
        select(PriceHistory)
        .where(PriceHistory.price_plan_id == price_id)
        .order_by(PriceHistory.recorded_at.desc())
        .limit(limit)
    )
    result = await db.execute(query)
    history = result.scalars().all()

    return [PriceHistoryResponse.model_validate(h) for h in history]


def _convert_price_tiers(price_tiers: dict | None) -> list[dict] | None:
    """Convert price_tiers dict to list format for calculation.

    Converts from: {"tier1_0_120": 29.80, "tier2_120_300": 36.40, "tier3_over_300": 40.49}
    To: [{"min": 0, "max": 120, "price": 29.80}, ...]
    """
    if not price_tiers:
        return None

    tiers = []
    for key, price in price_tiers.items():
        if "tier1" in key or "0_120" in key:
            tiers.append({"min": 0, "max": 120, "price": float(price)})
        elif "tier2" in key or "120_300" in key:
            tiers.append({"min": 120, "max": 300, "price": float(price)})
        elif "tier3" in key or "over_300" in key:
            tiers.append({"min": 300, "max": 999999, "price": float(price)})

    return tiers if tiers else None


@router.post("/compare", response_model=PriceCompareResponse)
async def compare_prices(db: DbSession, data: PriceCompareRequest):
    """요금제 비교."""
    comparisons: list[PriceCompareItem] = []
    cheapest_total: Decimal | None = None
    cheapest_plan_id: int | None = None

    for plan_id in data.plan_ids:
        query = select(PricePlan).where(PricePlan.id == plan_id)
        result = await db.execute(query)
        plan = result.scalar_one_or_none()

        if not plan:
            continue

        company = await db.scalar(select(Company).where(Company.id == plan.company_id))

        # Calculate estimated cost
        base_charge = float(plan.base_charge or 0)
        unit_price = float(plan.unit_price or 0)
        fuel = float(plan.fuel_adjustment or 0)
        renewable = float(plan.renewable_surcharge or 0)

        # Convert price_tiers to list format
        price_tiers_list = _convert_price_tiers(plan.price_tiers)

        estimated = calculate_monthly_bill(
            usage_kwh=data.usage_kwh,
            base_charge=base_charge,
            price_tiers=price_tiers_list,
            unit_price=unit_price,
            fuel_adjustment=fuel,
            renewable_surcharge=renewable,
        )

        total = Decimal(str(estimated))

        if cheapest_total is None or total < cheapest_total:
            cheapest_total = total
            cheapest_plan_id = plan_id

        # Calculate usage cost for display
        if price_tiers_list:
            usage_cost = estimated - base_charge - (data.usage_kwh * (fuel + renewable))
        else:
            usage_cost = data.usage_kwh * unit_price

        comparisons.append(
            PriceCompareItem(
                plan_id=plan.id,
                company_name=company.name_en if company else "Unknown",
                plan_name=plan.plan_name_ja,
                base_charge=plan.base_charge,
                unit_price=plan.unit_price,
                estimated_monthly_cost=Decimal(str(usage_cost)),
                fuel_adjustment=plan.fuel_adjustment,
                renewable_surcharge=plan.renewable_surcharge,
                total_estimated=total,
            )
        )

    return PriceCompareResponse(
        usage_kwh=data.usage_kwh,
        comparisons=comparisons,
        cheapest_plan_id=cheapest_plan_id,
    )
