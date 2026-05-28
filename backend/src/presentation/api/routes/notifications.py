from datetime import datetime

from fastapi import APIRouter, BackgroundTasks, Depends, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.application.dto.schemas import NotificationRead
from src.domain.entities.enums import NotificationStatus
from src.infrastructure.database.models import NotificationModel
from src.infrastructure.database.session import get_db
from src.infrastructure.email.smtp_service import SmtpEmailService

router = APIRouter()


@router.get("", response_model=list[NotificationRead])
def list_notifications(db: Session = Depends(get_db)) -> list[NotificationModel]:
    return list(db.scalars(select(NotificationModel).order_by(NotificationModel.created_at.desc())))


@router.get("/history", response_model=list[NotificationRead])
def notification_history(db: Session = Depends(get_db)) -> list[NotificationModel]:
    return list(db.scalars(select(NotificationModel).order_by(NotificationModel.created_at.desc())))


@router.post("/send", response_model=NotificationRead, status_code=status.HTTP_202_ACCEPTED)
def send_notification(
    payload: dict,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
) -> NotificationModel:
    notification = NotificationModel(
        client_id=payload.get("client_id"),
        shipment_id=payload.get("shipment_id"),
        notification_type=payload.get("notification_type", "STATUS_ALERT"),
        subject=payload["subject"],
        body=payload["body"],
        status=NotificationStatus.PENDING.value,
    )
    db.add(notification)
    db.commit()
    db.refresh(notification)

    recipients = payload.get("recipients", [])
    if recipients:
        background_tasks.add_task(
            SmtpEmailService().send_html_email,
            recipients,
            notification.subject,
            notification.body,
            None,
        )
        notification.status = NotificationStatus.SENT.value
        notification.sent_at = datetime.utcnow()
        db.commit()
        db.refresh(notification)

    return notification
