import re
from datetime import datetime, timedelta, date
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func as sa_func
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.academic import (
    Routine, Course, Enrollment, AttendanceSession,
    AttendanceRecord, AttendanceStatus, Result, DayOfWeek,
)
from app.schemas.academic import ChatRequest, ChatResponse

router = APIRouter(prefix="/assistant", tags=["assistant"])

# Bangla keyword mapping
BANGLA_KEYWORDS = {
    "class": ["ক্লাস", "কلاس"],
    "tomorrow": ["আগামীকাল", "কাল", "আগামী কাল"],
    "today": ["আজ", "আজকে"],
    "attendance": ["উপস্থিতি", "হাজিরা", "এটেন্ডেন্স"],
    "result": ["রেজাল্ট", "ফলাফল", "রেজাল্ট"],
    "teacher": ["শিক্ষক", "স্যার", "টিচার"],
    "cgpa": ["সিজিপিএ", "জিপিএ"],
    "next": ["পরবর্তী", "নেক্সট"],
    "how_much": ["কত", "কতো"],
    "what": ["কি", "কী"],
    "when": ["কখন", "কবে"],
    "who": ["কে"],
}

DAY_MAP = {
    "saturday": DayOfWeek.SATURDAY, "sunday": DayOfWeek.SUNDAY,
    "monday": DayOfWeek.MONDAY, "tuesday": DayOfWeek.TUESDAY,
    "wednesday": DayOfWeek.WEDNESDAY, "thursday": DayOfWeek.THURSDAY,
    "friday": DayOfWeek.FRIDAY,
}


def _detect_query_type(message: str) -> str:
    msg = message.lower().strip()

    # Check for course code pattern (CSE-301, MAT-201, etc.)
    if re.search(r'[a-z]{2,4}-\d{3}', msg):
        if any(kw in msg for kw in ["teacher", "কে", "শিক্ষক", "স্যার"]):
            return "course_teacher"
        if any(kw in msg for kw in ["routine", "schedule", "time"]):
            return "course_schedule"

    # Attendance queries
    if any(kw in msg for kw in ["attendance", "উপস্থিতি", "হাজিরা", "এটেন্ডেন্স"]):
        if any(kw in msg for kw in ["how_much", "কত", "percentage"]):
            return "attendance_stats"
        return "attendance_stats"

    # Tomorrow's class
    if any(kw in msg for kw in ["tomorrow", "কাল", "আগামীকাল"]):
        if any(kw in msg for kw in ["class", "ক্লাস", "কلاس"]):
            return "tomorrow_class"

    # Today's class
    if any(kw in msg for kw in ["today", "আজ", "আজকে"]):
        if any(kw in msg for kw in ["class", "ক্লাস"]):
            return "today_class"

    # Next class
    if any(kw in msg for kw in ["next", "পরবর্তী", "নেক্সট"]):
        if any(kw in msg for kw in ["class", "ক্লাস"]):
            return "next_class"

    # CGPA
    if any(kw in msg for kw in ["cgpa", "সিজিপিএ", "জিপিএ"]):
        return "cgpa"

    # Results
    if any(kw in msg for kw in ["result", "রেজাল্ট", "ফলাফল"]):
        return "results"

    return "unknown"


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query_type = _detect_query_type(request.message)
    reply = ""

    try:
        if query_type == "tomorrow_class":
            tomorrow = (date.today() + timedelta(days=1)).strftime("%A")
            day_enum = DAY_MAP.get(tomorrow.lower())
            if day_enum:
                result = await db.execute(
                    select(Routine, Course)
                    .join(Course)
                    .join(Enrollment)
                    .where(
                        Enrollment.student_id == current_user.id,
                        Routine.day_of_week == day_enum,
                    )
                )
                rows = result.all()
                if rows:
                    classes = [f"{c.code} ({c.name}) at {r.start_time.strftime('%I:%M %p')} in Room {r.room}" for r, c in rows]
                    reply = f"Tomorrow you have: {'; '.join(classes)}"
                else:
                    reply = "No classes scheduled for tomorrow."
            else:
                reply = "Could not determine tomorrow's day."

        elif query_type == "today_class":
            today = date.today().strftime("%A")
            day_enum = DAY_MAP.get(today.lower())
            if day_enum:
                result = await db.execute(
                    select(Routine, Course)
                    .join(Course)
                    .join(Enrollment)
                    .where(
                        Enrollment.student_id == current_user.id,
                        Routine.day_of_week == day_enum,
                    )
                )
                rows = result.all()
                if rows:
                    classes = [f"{c.code} at {r.start_time.strftime('%I:%M %p')} in Room {r.room}" for r, c in rows]
                    reply = f"Today's classes: {'; '.join(classes)}"
                else:
                    reply = "No classes today. Enjoy! 🎉"
            else:
                reply = "Could not determine today's day."

        elif query_type == "attendance_stats":
            # Get overall attendance across all enrolled courses
            enrollments = await db.execute(select(Enrollment).where(Enrollment.student_id == current_user.id))
            enrolled_courses = enrollments.scalars().all()

            if not enrolled_courses:
                reply = "You are not enrolled in any courses yet."
            else:
                total_present = 0
                total_sessions = 0
                course_details = []
                for enr in enrolled_courses:
                    sessions_count = await db.execute(
                        select(sa_func.count(AttendanceSession.id)).where(AttendanceSession.course_id == enr.course_id)
                    )
                    ts = sessions_count.scalar() or 0
                    present_count = await db.execute(
                        select(sa_func.count(AttendanceRecord.id))
                        .join(AttendanceSession)
                        .where(
                            AttendanceRecord.student_id == current_user.id,
                            AttendanceSession.course_id == enr.course_id,
                            AttendanceRecord.status == AttendanceStatus.PRESENT,
                        )
                    )
                    pc = present_count.scalar() or 0
                    total_present += pc
                    total_sessions += ts
                    cr = await db.execute(select(Course).where(Course.id == enr.course_id))
                    course = cr.scalar_one_or_none()
                    pct = round(pc / ts * 100, 1) if ts > 0 else 0
                    course_details.append(f"{course.code}: {pct}%")

                overall = round(total_present / total_sessions * 100, 1) if total_sessions > 0 else 0
                reply = f"Your overall attendance is {overall}%. Breakdown: {'; '.join(course_details)}"

        elif query_type == "course_teacher":
            match = re.search(r'([a-z]{2,4}-\d{3})', request.message.lower())
            if match:
                code = match.group(1).upper()
                result = await db.execute(
                    select(Course, User).join(User, Course.teacher_id == User.id).where(Course.code.ilike(f"%{code}%"))
                )
                row = result.first()
                if row:
                    course, teacher = row
                    reply = f"{course.code} ({course.name}) is taught by {teacher.name}."
                else:
                    reply = f"Course {code} not found."
            else:
                reply = "Please specify a course code like CSE-301."

        elif query_type == "cgpa":
            results = await db.execute(select(Result).where(Result.student_id == current_user.id))
            all_results = results.scalars().all()
            if not all_results:
                reply = "No results available yet to calculate CGPA."
            else:
                course_results = {}
                for r in all_results:
                    if r.course_id not in course_results or r.created_at > course_results[r.course_id].created_at:
                        course_results[r.course_id] = r
                total_gp = sum((r.grade_point or 0) * 3 for r in course_results.values())
                total_credits = len(course_results) * 3
                cgpa = round(total_gp / total_credits, 2) if total_credits > 0 else 0
                reply = f"Your current CGPA is {cgpa} based on {len(course_results)} courses."

        elif query_type == "results":
            results = await db.execute(
                select(Result, Course).join(Course).where(Result.student_id == current_user.id).order_by(Result.created_at.desc()).limit(5)
            )
            rows = results.all()
            if rows:
                items = [f"{c.code}: {r.grade} ({r.marks_obtained}/{r.total_marks})" for r, c in rows]
                reply = f"Your recent results: {'; '.join(items)}"
            else:
                reply = "No results published yet."

        elif query_type == "next_class":
            today = date.today().strftime("%A")
            day_enum = DAY_MAP.get(today.lower())
            if day_enum:
                now = datetime.now().time()
                result = await db.execute(
                    select(Routine, Course)
                    .join(Course)
                    .join(Enrollment)
                    .where(
                        Enrollment.student_id == current_user.id,
                        Routine.day_of_week == day_enum,
                        Routine.start_time > now,
                    ).order_by(Routine.start_time).limit(1)
                )
                row = result.first()
                if row:
                    r, c = row
                    reply = f"Next class: {c.code} at {r.start_time.strftime('%I:%M %p')} in Room {r.room}"
                else:
                    reply = "No more classes today. You're free! 🎉"
            else:
                reply = "Could not determine current schedule."

        else:
            reply = "I can help with: 'amar kal ki class?', 'amar attendance koto?', 'CSE-301 er teacher ke?', 'amar cgpa koto?', 'amar result dekhao'. Try asking in Bangla or English! 😊"

    except Exception as e:
        reply = f"Sorry, I encountered an error processing your query. Please try again."

    return ChatResponse(reply=reply, query_type=query_type)
