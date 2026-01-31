"""Alert schemas for API validation."""

from datetime import datetime

from pydantic import BaseModel, Field, EmailStr


class AlertRecipientCreate(BaseModel):
    """Schema for creating an alert recipient."""

    email: EmailStr = Field(..., description="이메일 주소")
    name: str | None = Field(None, max_length=100, description="수신자 이름")


class AlertRecipientResponse(BaseModel):
    """Schema for alert recipient response."""

    id: int
    email: str
    name: str | None
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class AlertSettingBase(BaseModel):
    """Base schema for AlertSetting."""

    alert_type: str = Field(
        ...,
        description="알림 유형 (crawl_failure, price_change, weekly_report)",
    )
    is_enabled: bool = Field(default=True, description="활성화 여부")


class AlertSettingCreate(AlertSettingBase):
    """Schema for creating an alert setting."""

    recipients: list[AlertRecipientCreate] = Field(
        default_factory=list, description="수신자 목록"
    )


class AlertSettingUpdate(BaseModel):
    """Schema for updating an alert setting."""

    is_enabled: bool | None = None


class AlertSettingResponse(AlertSettingBase):
    """Schema for alert setting response."""

    id: int
    recipients: list[AlertRecipientResponse] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
