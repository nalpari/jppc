"""Alerts API endpoints."""

from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import select

from app.api.deps import DbSession
from app.models import AlertSetting, AlertRecipient
from app.schemas import (
    AlertSettingCreate,
    AlertSettingUpdate,
    AlertSettingResponse,
    AlertRecipientCreate,
    AlertRecipientResponse,
)

router = APIRouter()


@router.get("", response_model=list[AlertSettingResponse])
async def list_alert_settings(db: DbSession):
    """알림 설정 목록 조회."""
    query = select(AlertSetting)
    result = await db.execute(query)
    settings = result.scalars().all()

    items = []
    for setting in settings:
        # Get recipients
        recipients_query = select(AlertRecipient).where(
            AlertRecipient.alert_setting_id == setting.id
        )
        recipients_result = await db.execute(recipients_query)
        recipients = recipients_result.scalars().all()

        setting_dict = {
            **setting.__dict__,
            "recipients": [AlertRecipientResponse.model_validate(r) for r in recipients],
        }
        items.append(AlertSettingResponse.model_validate(setting_dict))

    return items


@router.get("/{alert_type}", response_model=AlertSettingResponse)
async def get_alert_setting(db: DbSession, alert_type: str):
    """알림 설정 상세 조회."""
    query = select(AlertSetting).where(AlertSetting.alert_type == alert_type)
    result = await db.execute(query)
    setting = result.scalar_one_or_none()

    if not setting:
        raise HTTPException(status_code=404, detail="Alert setting not found")

    # Get recipients
    recipients_query = select(AlertRecipient).where(
        AlertRecipient.alert_setting_id == setting.id
    )
    recipients_result = await db.execute(recipients_query)
    recipients = recipients_result.scalars().all()

    setting_dict = {
        **setting.__dict__,
        "recipients": [AlertRecipientResponse.model_validate(r) for r in recipients],
    }
    return AlertSettingResponse.model_validate(setting_dict)


@router.post("", response_model=AlertSettingResponse, status_code=201)
async def create_alert_setting(db: DbSession, data: AlertSettingCreate):
    """알림 설정 생성."""
    # Check for duplicate
    existing = await db.scalar(
        select(AlertSetting).where(AlertSetting.alert_type == data.alert_type)
    )
    if existing:
        raise HTTPException(status_code=400, detail="Alert type already exists")

    setting = AlertSetting(
        alert_type=data.alert_type,
        is_enabled=data.is_enabled,
    )
    db.add(setting)
    await db.flush()
    await db.refresh(setting)

    # Add recipients
    recipients = []
    for recipient_data in data.recipients:
        recipient = AlertRecipient(
            alert_setting_id=setting.id,
            email=recipient_data.email,
            name=recipient_data.name,
        )
        db.add(recipient)
        await db.flush()
        await db.refresh(recipient)
        recipients.append(AlertRecipientResponse.model_validate(recipient))

    setting_dict = {**setting.__dict__, "recipients": recipients}
    return AlertSettingResponse.model_validate(setting_dict)


@router.patch("/{alert_type}", response_model=AlertSettingResponse)
async def update_alert_setting(db: DbSession, alert_type: str, data: AlertSettingUpdate):
    """알림 설정 수정."""
    query = select(AlertSetting).where(AlertSetting.alert_type == alert_type)
    result = await db.execute(query)
    setting = result.scalar_one_or_none()

    if not setting:
        raise HTTPException(status_code=404, detail="Alert setting not found")

    if data.is_enabled is not None:
        setting.is_enabled = data.is_enabled

    await db.flush()
    await db.refresh(setting)

    # Get recipients
    recipients_query = select(AlertRecipient).where(
        AlertRecipient.alert_setting_id == setting.id
    )
    recipients_result = await db.execute(recipients_query)
    recipients = recipients_result.scalars().all()

    setting_dict = {
        **setting.__dict__,
        "recipients": [AlertRecipientResponse.model_validate(r) for r in recipients],
    }
    return AlertSettingResponse.model_validate(setting_dict)


@router.post("/{alert_type}/recipients", response_model=AlertRecipientResponse, status_code=201)
async def add_recipient(db: DbSession, alert_type: str, data: AlertRecipientCreate):
    """알림 수신자 추가."""
    setting = await db.scalar(
        select(AlertSetting).where(AlertSetting.alert_type == alert_type)
    )
    if not setting:
        raise HTTPException(status_code=404, detail="Alert setting not found")

    recipient = AlertRecipient(
        alert_setting_id=setting.id,
        email=data.email,
        name=data.name,
    )
    db.add(recipient)
    await db.flush()
    await db.refresh(recipient)

    return AlertRecipientResponse.model_validate(recipient)


@router.delete("/{alert_type}/recipients/{recipient_id}", status_code=204)
async def remove_recipient(db: DbSession, alert_type: str, recipient_id: int):
    """알림 수신자 삭제."""
    query = (
        select(AlertRecipient)
        .join(AlertSetting)
        .where(
            AlertSetting.alert_type == alert_type,
            AlertRecipient.id == recipient_id,
        )
    )
    result = await db.execute(query)
    recipient = result.scalar_one_or_none()

    if not recipient:
        raise HTTPException(status_code=404, detail="Recipient not found")

    await db.delete(recipient)
