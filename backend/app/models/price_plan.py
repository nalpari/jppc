"""Price Plan and Price History models - 요금제 및 요금 이력."""

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import String, Text, Boolean, DateTime, Numeric, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base

if TYPE_CHECKING:
    from app.models.company import Company


class PricePlan(Base):
    """요금제 모델.

    Attributes:
        id: 고유 식별자
        company_id: 전력회사 ID
        plan_code: 요금제 코드
        plan_name_ja: 일본어 요금제명
        plan_name_en: 영어 요금제명
        plan_type: 요금제 유형 (residential, commercial, industrial)
        contract_type: 계약 유형
        base_charge: 기본요금 (엔)
        unit_price: 단위요금 (엔/kWh)
        price_tiers: 단계별 요금 (JSON)
        time_of_use: 시간대별 요금 (JSON)
        fuel_adjustment: 연료비 조정액
        renewable_surcharge: 재생에너지 부담금
        effective_date: 적용 시작일
        source_url: 정보 출처 URL
        raw_data: 크롤링 원본 데이터 (JSON)
        is_current: 현행 요금제 여부
        created_at: 생성일시
        updated_at: 수정일시
    """

    __tablename__ = "price_plans"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    company_id: Mapped[int] = mapped_column(
        ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True
    )
    plan_code: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    plan_name_ja: Mapped[str] = mapped_column(String(200), nullable=False)
    plan_name_en: Mapped[str | None] = mapped_column(String(200), nullable=True)
    plan_type: Mapped[str] = mapped_column(
        String(50), default="residential", nullable=False
    )  # residential, commercial, industrial
    contract_type: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Pricing fields
    base_charge: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    unit_price: Mapped[Decimal | None] = mapped_column(Numeric(10, 4), nullable=True)
    price_tiers: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    time_of_use: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    fuel_adjustment: Mapped[Decimal | None] = mapped_column(Numeric(10, 4), nullable=True)
    renewable_surcharge: Mapped[Decimal | None] = mapped_column(Numeric(10, 4), nullable=True)

    # Metadata
    effective_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    source_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    raw_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    is_current: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    company: Mapped["Company"] = relationship("Company", back_populates="price_plans")
    history: Mapped[list["PriceHistory"]] = relationship(
        "PriceHistory", back_populates="price_plan", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<PricePlan(code={self.plan_code}, name={self.plan_name_ja})>"


class PriceHistory(Base):
    """요금 변동 이력 모델.

    요금제의 가격 변동을 추적합니다.
    """

    __tablename__ = "price_history"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    price_plan_id: Mapped[int] = mapped_column(
        ForeignKey("price_plans.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Price snapshot
    base_charge: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    unit_price: Mapped[Decimal | None] = mapped_column(Numeric(10, 4), nullable=True)
    price_tiers: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    fuel_adjustment: Mapped[Decimal | None] = mapped_column(Numeric(10, 4), nullable=True)
    renewable_surcharge: Mapped[Decimal | None] = mapped_column(Numeric(10, 4), nullable=True)

    # Change tracking
    change_type: Mapped[str] = mapped_column(
        String(20), nullable=False
    )  # created, updated, price_change
    change_details: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    recorded_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False, index=True
    )

    # Relationships
    price_plan: Mapped["PricePlan"] = relationship("PricePlan", back_populates="history")

    def __repr__(self) -> str:
        return f"<PriceHistory(plan_id={self.price_plan_id}, recorded_at={self.recorded_at})>"
