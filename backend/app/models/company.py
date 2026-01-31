"""Company model - 전력회사 정보."""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import String, Text, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base

if TYPE_CHECKING:
    from app.models.price_plan import PricePlan
    from app.models.crawl_log import CrawlLog


class Company(Base):
    """전력회사 모델.

    Attributes:
        id: 고유 식별자
        code: 회사 코드 (tepco, chubu, kepco, chugoku)
        name_ja: 일본어 회사명
        name_en: 영어 회사명
        name_ko: 한국어 회사명
        website_url: 공식 웹사이트 URL
        price_page_url: 요금 정보 페이지 URL
        region: 관할 지역
        is_active: 활성화 여부
        created_at: 생성일시
        updated_at: 수정일시
    """

    __tablename__ = "companies"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    name_ja: Mapped[str] = mapped_column(String(100), nullable=False)
    name_en: Mapped[str] = mapped_column(String(100), nullable=False)
    name_ko: Mapped[str] = mapped_column(String(100), nullable=True)
    website_url: Mapped[str] = mapped_column(String(500), nullable=False)
    price_page_url: Mapped[str] = mapped_column(String(500), nullable=False)
    region: Mapped[str] = mapped_column(String(100), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    price_plans: Mapped[list["PricePlan"]] = relationship(
        "PricePlan", back_populates="company", cascade="all, delete-orphan"
    )
    crawl_logs: Mapped[list["CrawlLog"]] = relationship(
        "CrawlLog", back_populates="company", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Company(code={self.code}, name={self.name_en})>"
