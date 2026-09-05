from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from app.core.database import get_db
from app.core.dependencies import get_current_user, require_role
from app.models.user import User, UserRole
from app.models.academic import Course, Enrollment
from app.schemas.academic import CourseCreate, CourseResponse, EnrollmentCreate, EnrollmentResponse

router = APIRouter(prefix="/courses", tags=["courses"])


@router.post("/", response_model=CourseResponse, status_code=status.HTTP_201_CREATED)
async def create_course(
    data: CourseCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.TEACHER, UserRole.ADMIN)),
):
    course = Course(**data.model_dump(), teacher_id=current_user.id)
    db.add(course)
    await db.flush()
    await db.refresh(course)
    return course


@router.get("/", response_model=List[CourseResponse])
async def list_courses(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role == UserRole.STUDENT:
        result = await db.execute(
            select(Course).join(Enrollment).where(Enrollment.student_id == current_user.id)
        )
    elif current_user.role == UserRole.TEACHER:
        result = await db.execute(select(Course).where(Course.teacher_id == current_user.id))
    else:
        result = await db.execute(select(Course))
    return result.scalars().all()


@router.get("/{course_id}", response_model=CourseResponse)
async def get_course(course_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(Course).where(Course.id == course_id))
    course = result.scalar_one_or_none()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course


@router.post("/enroll", response_model=EnrollmentResponse, status_code=status.HTTP_201_CREATED)
async def enroll_student(
    data: EnrollmentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.TEACHER)),
):
    existing = await db.execute(
        select(Enrollment).where(
            Enrollment.student_id == data.student_id,
            Enrollment.course_id == data.course_id,
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Already enrolled")
    enrollment = Enrollment(**data.model_dump())
    db.add(enrollment)
    await db.flush()
    await db.refresh(enrollment)
    return enrollment


@router.get("/enrolled/me", response_model=List[CourseResponse])
async def my_enrolled_courses(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Course).join(Enrollment).where(Enrollment.student_id == current_user.id)
    )
    return result.scalars().all()
