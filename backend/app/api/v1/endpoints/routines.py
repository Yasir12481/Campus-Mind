from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from app.core.database import get_db
from app.core.dependencies import get_current_user, require_role
from app.models.user import User, UserRole
from app.models.academic import Routine, Course, Enrollment
from app.schemas.academic import RoutineCreate, RoutineUpdate, RoutineResponse

router = APIRouter(prefix="/routines", tags=["routines"])


@router.post("/", response_model=RoutineResponse)
async def create_routine(
    data: RoutineCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.TEACHER, UserRole.ADMIN)),
):
    routine = Routine(**data.model_dump())
    db.add(routine)
    await db.flush()
    await db.refresh(routine)
    return routine


@router.get("/me", response_model=List[RoutineResponse])
async def my_routine(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role == UserRole.STUDENT:
        result = await db.execute(
            select(Routine).join(Course).join(Enrollment).where(Enrollment.student_id == current_user.id)
        )
    elif current_user.role == UserRole.TEACHER:
        result = await db.execute(
            select(Routine).join(Course).where(Course.teacher_id == current_user.id)
        )
    else:
        result = await db.execute(select(Routine))
    return result.scalars().all()


@router.get("/course/{course_id}", response_model=List[RoutineResponse])
async def course_routine(course_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(Routine).where(Routine.course_id == course_id))
    return result.scalars().all()


@router.patch("/{routine_id}", response_model=RoutineResponse)
async def update_routine(
    routine_id: int,
    data: RoutineUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.TEACHER, UserRole.ADMIN)),
):
    result = await db.execute(select(Routine).where(Routine.id == routine_id))
    routine = result.scalar_one_or_none()
    if not routine:
        raise HTTPException(status_code=404, detail="Routine not found")
    # Verify ownership via course
    course_result = await db.execute(select(Course).where(Course.id == routine.course_id))
    course = course_result.scalar_one_or_none()
    if current_user.role == UserRole.TEACHER and course.teacher_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your course")
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(routine, field, value)
    await db.flush()
    await db.refresh(routine)
    return routine


@router.delete("/{routine_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_routine(
    routine_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.TEACHER, UserRole.ADMIN)),
):
    result = await db.execute(select(Routine).where(Routine.id == routine_id))
    routine = result.scalar_one_or_none()
    if not routine:
        raise HTTPException(status_code=404, detail="Routine not found")
    course_result = await db.execute(select(Course).where(Course.id == routine.course_id))
    course = course_result.scalar_one_or_none()
    if current_user.role == UserRole.TEACHER and course.teacher_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your course")
    await db.delete(routine)
