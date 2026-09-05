import uuid
import csv
import io
from datetime import datetime, timedelta, timezone, date
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func as sa_func
from typing import List
from app.core.database import get_db
from app.core.dependencies import get_current_user, require_role
from app.models.user import User, UserRole
from app.models.academic import (
    AttendanceSession, AttendanceRecord, Course, Enrollment,
    AttendanceMethod, AttendanceStatus,
)
from app.schemas.academic import (
    SessionCreate, SessionResponse, MarkAttendanceQR,
    MarkAttendanceFace, AttendanceRecordResponse, AttendanceStats,
)

router = APIRouter(prefix="/attendance", tags=["attendance"])


def _generate_qr_token() -> str:
    return uuid.uuid4().hex[:12]


@router.post("/sessions", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
async def create_session(
    data: SessionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.TEACHER)),
):
    # Verify teacher owns this course
    result = await db.execute(select(Course).where(Course.id == data.course_id, Course.teacher_id == current_user.id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=403, detail="You don't teach this course")

    qr_token = _generate_qr_token()
    session = AttendanceSession(
        course_id=data.course_id,
        teacher_id=current_user.id,
        qr_code=qr_token,
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=data.duration_minutes),
        is_active=True,
    )
    db.add(session)
    await db.flush()
    await db.refresh(session)
    return session


@router.get("/sessions/{session_id}", response_model=SessionResponse)
async def get_session(session_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(AttendanceSession).where(AttendanceSession.id == session_id))
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


@router.post("/mark/qr", response_model=AttendanceRecordResponse)
async def mark_attendance_qr(
    data: MarkAttendanceQR,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Get active session
    result = await db.execute(
        select(AttendanceSession).where(
            AttendanceSession.id == data.session_id,
            AttendanceSession.is_active == True,
        )
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=400, detail="Invalid or expired session")
    if session.qr_code != data.qr_code:
        raise HTTPException(status_code=400, detail="Invalid QR code")
    if datetime.now(timezone.utc) > session.expires_at:
        raise HTTPException(status_code=400, detail="Session expired")

    # Check student is enrolled
    enr = await db.execute(
        select(Enrollment).where(
            Enrollment.student_id == current_user.id,
            Enrollment.course_id == session.course_id,
        )
    )
    if not enr.scalar_one_or_none():
        raise HTTPException(status_code=403, detail="Not enrolled in this course")

    # Check duplicate
    dup = await db.execute(
        select(AttendanceRecord).where(
            AttendanceRecord.session_id == data.session_id,
            AttendanceRecord.student_id == current_user.id,
        )
    )
    if dup.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Already marked")

    record = AttendanceRecord(
        session_id=data.session_id,
        student_id=current_user.id,
        method=AttendanceMethod.QR,
        status=AttendanceStatus.PRESENT,
    )
    db.add(record)
    await db.flush()
    await db.refresh(record)
    return record


@router.post("/mark/face", response_model=AttendanceRecordResponse)
async def mark_attendance_face(
    data: MarkAttendanceFace,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Placeholder: In production, decode base64 → MediaPipe → compare embeddings
    # For now, accept any valid session as present (face verification is bonus)
    result = await db.execute(
        select(AttendanceSession).where(
            AttendanceSession.id == data.session_id,
            AttendanceSession.is_active == True,
        )
    )
    session = result.scalar_one_or_none()
    if not session or datetime.now(timezone.utc) > session.expires_at:
        raise HTTPException(status_code=400, detail="Invalid or expired session")

    record = AttendanceRecord(
        session_id=data.session_id,
        student_id=current_user.id,
        method=AttendanceMethod.FACE,
        status=AttendanceStatus.PRESENT,
    )
    db.add(record)
    await db.flush()
    await db.refresh(record)
    return record


@router.get("/me", response_model=List[AttendanceRecordResponse])
async def my_attendance(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(AttendanceRecord).where(AttendanceRecord.student_id == current_user.id)
    )
    return result.scalars().all()


@router.get("/course/{course_id}/stats", response_model=AttendanceStats)
async def attendance_stats(
    course_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Total sessions for this course
    total_result = await db.execute(
        select(sa_func.count(AttendanceSession.id)).where(AttendanceSession.course_id == course_id)
    )
    total_classes = total_result.scalar() or 0

    # Student's records for this course
    records_result = await db.execute(
        select(AttendanceRecord)
        .join(AttendanceSession)
        .where(
            AttendanceRecord.student_id == current_user.id,
            AttendanceSession.course_id == course_id,
        )
    )
    records = records_result.scalars().all()

    present = sum(1 for r in records if r.status == AttendanceStatus.PRESENT)
    late = sum(1 for r in records if r.status == AttendanceStatus.LATE)
    absent = total_classes - present - late
    percentage = ((present + late) / total_classes * 100) if total_classes > 0 else 0.0

    # Bunk calculator: how many more can skip while staying >= 75%
    can_bunk = 0
    if total_classes > 0:
        min_required = 0.75
        # (present + late) / (total_classes + x) >= min_required
        # x <= (present + late) / min_required - total_classes
        max_total = int((present + late) / min_required)
        can_bunk = max(0, max_total - total_classes)

    return AttendanceStats(
        course_id=course_id,
        total_classes=total_classes,
        present=present,
        absent=absent,
        late=late,
        percentage=round(percentage, 2),
        can_bunk=can_bunk,
    )


@router.get("/export/{course_id}")
async def export_attendance_csv(
    course_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(AttendanceRecord, AttendanceSession)
        .join(AttendanceSession)
        .where(AttendanceSession.course_id == course_id)
    )
    rows = result.all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["student_id", "session_id", "date", "method", "status", "marked_at"])
    for record, session in rows:
        writer.writerow([
            record.student_id, record.session_id, str(session.session_date),
            record.method.value, record.status.value, str(record.marked_at),
        ])

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=attendance_course_{course_id}.csv"},
    )
