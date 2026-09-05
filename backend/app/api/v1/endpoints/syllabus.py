from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from app.core.database import get_db
from app.core.dependencies import get_current_user, require_role
from app.models.user import User, UserRole
from app.models.academic import SyllabusTopic
from app.schemas.academic import SyllabusTopicCreate, SyllabusTopicResponse

router = APIRouter(prefix="/syllabus", tags=["syllabus"])


@router.post("/", response_model=SyllabusTopicResponse)
async def create_topic(
    data: SyllabusTopicCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.TEACHER, UserRole.ADMIN)),
):
    topic = SyllabusTopic(**data.model_dump())
    db.add(topic)
    await db.flush()
    await db.refresh(topic)
    return topic


@router.get("/course/{course_id}", response_model=List[SyllabusTopicResponse])
async def course_syllabus(course_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(SyllabusTopic).where(SyllabusTopic.course_id == course_id).order_by(SyllabusTopic.week_number))
    return result.scalars().all()


@router.patch("/{topic_id}/complete", response_model=SyllabusTopicResponse)
async def toggle_complete(
    topic_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.TEACHER, UserRole.ADMIN)),
):
    result = await db.execute(select(SyllabusTopic).where(SyllabusTopic.id == topic_id))
    topic = result.scalar_one_or_none()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    topic.is_completed = not topic.is_completed
    await db.flush()
    await db.refresh(topic)
    return topic
