from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from app.core.database import get_db
from app.core.dependencies import get_current_user, require_role
from app.models.user import User, UserRole
from app.models.academic import Result, Course, Enrollment
from app.schemas.academic import ResultCreate, ResultResponse, CGPAResponse

router = APIRouter(prefix="/results", tags=["results"])

GRADE_SCALE = [
    (4.00, "A+", 80), (3.75, "A", 75), (3.50, "A-", 70),
    (3.25, "B+", 65), (3.00, "B", 60), (2.75, "B-", 55),
    (2.50, "C+", 50), (2.25, "C", 45), (2.00, "D", 40),
    (0.00, "F", 0),
]


def _calc_grade(percentage: float) -> tuple[str, float]:
    for gp, grade, threshold in GRADE_SCALE:
        if percentage >= threshold:
            return grade, gp
    return "F", 0.0


@router.post("/", response_model=ResultResponse)
async def create_result(
    data: ResultCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.TEACHER, UserRole.ADMIN)),
):
    percentage = (data.marks_obtained / data.total_marks * 100) if data.total_marks > 0 else 0
    grade, gp = _calc_grade(percentage)

    result_entry = Result(
        **data.model_dump(),
        grade=grade,
        grade_point=gp,
    )
    db.add(result_entry)
    await db.flush()
    await db.refresh(result_entry)
    return result_entry


@router.get("/me", response_model=List[ResultResponse])
async def my_results(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Result).where(Result.student_id == current_user.id))
    return result.scalars().all()


@router.get("/me/cgpa", response_model=CGPAResponse)
async def my_cgpa(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Get latest result per course
    results = await db.execute(
        select(Result).where(Result.student_id == current_user.id)
    )
    all_results = results.scalars().all()

    # Group by course, take latest
    course_results = {}
    for r in all_results:
        if r.course_id not in course_results or r.created_at > course_results[r.course_id].created_at:
            course_results[r.course_id] = r

    total_weighted_gp = 0.0
    total_credits = 0
    courses_detail = []

    for cid, r in course_results.items():
        cr = await db.execute(select(Course).where(Course.id == cid))
        course = cr.scalar_one_or_none()
        credits = course.credits if course else 3
        total_weighted_gp += (r.grade_point or 0) * credits
        total_credits += credits
        courses_detail.append({
            "course_code": course.code if course else "Unknown",
            "grade": r.grade,
            "grade_point": r.grade_point,
            "credits": credits,
        })

    cgpa = round(total_weighted_gp / total_credits, 2) if total_credits > 0 else 0.0
    return CGPAResponse(cgpa=cgpa, total_credits=total_credits, courses=courses_detail)


@router.get("/course/{course_id}", response_model=List[ResultResponse])
async def course_results(
    course_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Result).where(Result.course_id == course_id))
    return result.scalars().all()
