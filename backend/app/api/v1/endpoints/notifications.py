from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from app.core.database import get_db
from app.core.dependencies import get_current_user, require_role
from app.models.user import User, UserRole
from app.models.academic import Notification
from app.schemas.academic import NotificationCreate, NotificationResponse

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.post("/", response_model=NotificationResponse)
async def create_notification(
    data: NotificationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.TEACHER, UserRole.ADMIN)),
):
    notif = Notification(**data.model_dump())
    db.add(notif)
    await db.flush()
    await db.refresh(notif)
    return notif


@router.get("/me", response_model=List[NotificationResponse])
async def my_notifications(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Notification).where(Notification.user_id == current_user.id).order_by(Notification.created_at.desc())
    )
    return result.scalars().all()


@router.patch("/{notif_id}/read", response_model=NotificationResponse)
async def mark_read(
    notif_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Notification).where(Notification.id == notif_id, Notification.user_id == current_user.id))
    notif = result.scalar_one_or_none()
    if notif:
        notif.is_read = True
        await db.flush()
        await db.refresh(notif)
    return notif
