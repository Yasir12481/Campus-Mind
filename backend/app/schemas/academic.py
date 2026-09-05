from pydantic import BaseModel
from typing import Optional, List
from datetime import date, time, datetime
from app.models.academic import DayOfWeek, AttendanceMethod, AttendanceStatus


# ── Course ──
class CourseCreate(BaseModel):
    code: str
    name: str
    credits: int = 3
    department: Optional[str] = None
    semester: Optional[str] = None

class CourseResponse(BaseModel):
    id: int
    code: str
    name: str
    credits: int
    department: Optional[str]
    teacher_id: Optional[int]
    semester: Optional[str]
    class Config:
        from_attributes = True


# ── Enrollment ──
class EnrollmentCreate(BaseModel):
    student_id: int
    course_id: int

class EnrollmentResponse(BaseModel):
    id: int
    student_id: int
    course_id: int
    class Config:
        from_attributes = True


# ── Routine ──
class RoutineCreate(BaseModel):
    course_id: int
    day_of_week: DayOfWeek
    start_time: time
    end_time: time
    room: str

class RoutineUpdate(BaseModel):
    day_of_week: Optional[DayOfWeek] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    room: Optional[str] = None

class RoutineResponse(BaseModel):
    id: int
    course_id: int
    day_of_week: DayOfWeek
    start_time: time
    end_time: time
    room: str
    course_code: Optional[str] = None
    course_name: Optional[str] = None
    class Config:
        from_attributes = True


# ── Attendance ──
class SessionCreate(BaseModel):
    course_id: int
    duration_minutes: int = 15

class SessionResponse(BaseModel):
    id: int
    course_id: int
    teacher_id: int
    qr_code: str
    session_date: date
    expires_at: datetime
    is_active: bool
    class Config:
        from_attributes = True

class MarkAttendanceQR(BaseModel):
    session_id: int
    qr_code: str

class MarkAttendanceFace(BaseModel):
    session_id: int
    face_image_base64: str

class AttendanceRecordResponse(BaseModel):
    id: int
    session_id: int
    student_id: int
    method: AttendanceMethod
    status: AttendanceStatus
    marked_at: datetime
    class Config:
        from_attributes = True

class AttendanceStats(BaseModel):
    course_id: int
    total_classes: int
    present: int
    absent: int
    late: int
    percentage: float
    can_bunk: int


# ── Result ──
class ResultCreate(BaseModel):
    student_id: int
    course_id: int
    exam_type: str
    marks_obtained: float
    total_marks: float

class ResultResponse(BaseModel):
    id: int
    student_id: int
    course_id: int
    exam_type: str
    marks_obtained: float
    total_marks: float
    grade: Optional[str]
    grade_point: Optional[float]
    class Config:
        from_attributes = True

class CGPAResponse(BaseModel):
    cgpa: float
    total_credits: int
    courses: List[dict]


# ── Syllabus ──
class SyllabusTopicCreate(BaseModel):
    course_id: int
    title: str
    week_number: Optional[int] = None

class SyllabusTopicResponse(BaseModel):
    id: int
    course_id: int
    title: str
    week_number: Optional[int]
    is_completed: bool
    class Config:
        from_attributes = True


# ── Notification ──
class NotificationCreate(BaseModel):
    user_id: int
    title: str
    message: str

class NotificationResponse(BaseModel):
    id: int
    user_id: int
    title: str
    message: str
    is_read: bool
    created_at: datetime
    class Config:
        from_attributes = True


# ── AI Assistant ──
class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    reply: str
    query_type: Optional[str] = None
