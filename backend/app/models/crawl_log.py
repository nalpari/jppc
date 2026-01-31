"""Crawl Log model - 크롤링 이력."""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import String, Text, DateTime, Integer, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base

if TYPE_CHECKING:
    from app.models.company import Company


class CrawlLog(Base):
    """크롤링 로그 모델.

    Attributes:
        id: 고유 식별자
        company_id: 전력회사 ID (null이면 전체 크롤링)
        status: 상태 (pending, running, success, failed, partial)
        trigger_type: 실행 유형 (scheduled, manual)
        started_at: 시작 시간
        finished_at: 종료 시간
        duration_seconds: 소요 시간 (초)
        plans_found: 발견된 요금제 수
        plans_updated: 업데이트된 요금제 수
        plans_created: 새로 생성된 요금제 수
        error_message: 에러 메시지
        error_details: 에러 상세 정보 (JSON)
        metadata: 추가 메타데이터 (JSON)
    """

    __tablename__ = "crawl_logs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    company_id: Mapped[int | None] = mapped_column(
        ForeignKey("companies.id", ondelete="SET NULL"), nullable=True, index=True
    )

    # Status
    status: Mapped[str] = mapped_column(
        String(20), default="pending", nullable=False, index=True
    )  # pending, running, success, failed, partial
    trigger_type: Mapped[str] = mapped_column(
        String(20), default="manual", nullable=False
    )  # scheduled, manual

    # Timing
    started_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False, index=True
    )
    finished_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    duration_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Results
    plans_found: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    plans_updated: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    plans_created: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Error handling
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    error_details: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    # Additional data
    metadata_: Mapped[dict | None] = mapped_column("metadata", JSON, nullable=True)

    # Relationships
    company: Mapped["Company | None"] = relationship("Company", back_populates="crawl_logs")

    def __repr__(self) -> str:
        return f"<CrawlLog(id={self.id}, status={self.status}, started_at={self.started_at})>"

    def mark_success(self, plans_found: int, plans_updated: int, plans_created: int) -> None:
        """Mark crawl as successful."""
        self.status = "success"
        self.finished_at = datetime.utcnow()
        self.duration_seconds = int((self.finished_at - self.started_at).total_seconds())
        self.plans_found = plans_found
        self.plans_updated = plans_updated
        self.plans_created = plans_created

    def mark_failed(self, error_message: str, error_details: dict | None = None) -> None:
        """Mark crawl as failed."""
        self.status = "failed"
        self.finished_at = datetime.utcnow()
        self.duration_seconds = int((self.finished_at - self.started_at).total_seconds())
        self.error_message = error_message
        self.error_details = error_details
