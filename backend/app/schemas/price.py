"""Price schemas for API validation."""

from datetime import datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, Field


class PricePlanBase(BaseModel):
    """Base schema for PricePlan."""

    plan_code: str = Field(..., min_length=1, max_length=50, description="요금제 코드")
    plan_name_ja: str = Field(..., min_length=1, max_length=200, description="일본어 요금제명")
    plan_name_en: str | None = Field(None, max_length=200, description="영어 요금제명")
    plan_type: str = Field(default="residential", description="요금제 유형")
    contract_type: str | None = Field(None, max_length=100, description="계약 유형")
    base_charge: Decimal | None = Field(None, description="기본요금 (엔)")
    unit_price: Decimal | None = Field(None, description="단위요금 (엔/kWh)")
    price_tiers: dict[str, Any] | None = Field(None, description="단계별 요금")
    time_of_use: dict[str, Any] | None = Field(None, description="시간대별 요금")
    fuel_adjustment: Decimal | None = Field(None, description="연료비 조정액")
    renewable_surcharge: Decimal | None = Field(None, description="재생에너지 부담금")
    effective_date: datetime | None = Field(None, description="적용 시작일")
    source_url: str | None = Field(None, max_length=500, description="정보 출처 URL")
    notes: str | None = Field(None, description="비고")


class PricePlanCreate(PricePlanBase):
    """Schema for creating a price plan."""

    company_id: int = Field(..., description="전력회사 ID")


class PricePlanUpdate(BaseModel):
    """Schema for updating a price plan."""

    plan_name_ja: str | None = Field(None, min_length=1, max_length=200)
    plan_name_en: str | None = Field(None, max_length=200)
    plan_type: str | None = None
    contract_type: str | None = Field(None, max_length=100)
    base_charge: Decimal | None = None
    unit_price: Decimal | None = None
    price_tiers: dict[str, Any] | None = None
    time_of_use: dict[str, Any] | None = None
    fuel_adjustment: Decimal | None = None
    renewable_surcharge: Decimal | None = None
    effective_date: datetime | None = None
    source_url: str | None = Field(None, max_length=500)
    notes: str | None = None
    is_current: bool | None = None


class PricePlanResponse(PricePlanBase):
    """Schema for price plan response."""

    id: int
    company_id: int
    company_name: str | None = None
    is_current: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PricePlanListResponse(BaseModel):
    """Schema for price plan list response."""

    items: list[PricePlanResponse]
    total: int
    page: int = 1
    page_size: int = 20


class PriceHistoryResponse(BaseModel):
    """Schema for price history response."""

    id: int
    price_plan_id: int
    base_charge: Decimal | None
    unit_price: Decimal | None
    price_tiers: dict[str, Any] | None
    fuel_adjustment: Decimal | None
    renewable_surcharge: Decimal | None
    change_type: str
    change_details: dict[str, Any] | None
    recorded_at: datetime

    model_config = {"from_attributes": True}


class PriceCompareRequest(BaseModel):
    """Schema for price comparison request."""

    plan_ids: list[int] = Field(..., min_length=2, max_length=10, description="비교할 요금제 ID 목록")
    usage_kwh: int = Field(default=300, ge=0, description="예상 사용량 (kWh)")


class PriceCompareItem(BaseModel):
    """Single item in price comparison."""

    plan_id: int
    company_name: str
    plan_name: str
    base_charge: Decimal | None
    unit_price: Decimal | None
    estimated_monthly_cost: Decimal | None
    fuel_adjustment: Decimal | None
    renewable_surcharge: Decimal | None
    total_estimated: Decimal | None


class PriceCompareResponse(BaseModel):
    """Schema for price comparison response."""

    usage_kwh: int
    comparisons: list[PriceCompareItem]
    cheapest_plan_id: int | None = None
