"""Alert Setting models - 알림 설정."""

from datetime import datetime

from sqlalchemy import String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class AlertSetting(Base):
    """알림 설정 모델.

    Attributes:
        id: 고유 식별자
        alert_type: 알림 유형 (crawl_failure, price_change, weekly_report)
        is_enabled: 활성화 여부
        created_at: 생성일시
        updated_at: 수정일시
    """

    __tablename__ = "alert_settings"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    alert_type: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False
    )  # crawl_failure, price_change, weekly_report
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    recipients: Mapped[list["AlertRecipient"]] = relationship(
        "AlertRecipient", back_populates="alert_setting", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<AlertSetting(type={self.alert_type}, enabled={self.is_enabled})>"


class AlertRecipient(Base):
    """알림 수신자 모델.

    Attributes:
        id: 고유 식별자
        alert_setting_id: 알림 설정 ID
        email: 이메일 주소
        name: 수신자 이름
        is_active: 활성화 여부
        created_at: 생성일시
    """

    __tablename__ = "alert_recipients"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    alert_setting_id: Mapped[int] = mapped_column(
        ForeignKey("alert_settings.id", ondelete="CASCADE"), nullable=False, index=True
    )
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    # Relationships
    alert_setting: Mapped["AlertSetting"] = relationship(
        "AlertSetting", back_populates="recipients"
    )

    def __repr__(self) -> str:
        return f"<AlertRecipient(email={self.email}, active={self.is_active})>"
