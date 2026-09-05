from datetime import datetime, date, time
from sqlalchemy import String, Integer, Float, Boolean, Date, Time, DateTime, ForeignKey, Enum, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.models.user import User
import enum


class Course(Base):
    __tablename__ = "courses"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)  # CSE-301
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    credits: Mapped[int] = mapped_column(Integer, default=3)
    department: Mapped[str] = mapped_column(String(100), nullable=True)
    teacher_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    semester: Mapped[str] = mapped_column(String(50), nullable=True)  # "Fall 2026"
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    teacher: Mapped[User | None] = relationship("User", foreign_keys=[teacher_id])
    enrollments: Mapped[list["Enrollment"]] = relationship(back_populates="course")
    routines: Mapped[list["Routine"]] = relationship(back_populates="course")


class Enrollment(Base):
    __tablename__ = "enrollments"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id"), nullable=False)
    enrolled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    student: Mapped[User] = relationship("User")
    course: Mapped[Course] = relationship(back_populates="enrollments")


class DayOfWeek(str, enum.Enum):
    SATURDAY = "Saturday"
    SUNDAY = "Sunday"
    MONDAY = "Monday"
    TUESDAY = "Tuesday"
    WEDNESDAY = "Wednesday"
    THURSDAY = "Thursday"
    FRIDAY = "Friday"


class Routine(Base):
    __tablename__ = "routines"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id"), nullable=False)
    day_of_week: Mapped[DayOfWeek] = mapped_column(Enum(DayOfWeek), nullable=False)
    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_time: Mapped[time] = mapped_column(Time, nullable=False)
    room: Mapped[str] = mapped_column(String(50), nullable=False)

    course: Mapped[Course] = relationship(back_populates="routines")


class AttendanceSession(Base):
    __tablename__ = "attendance_sessions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id"), nullable=False)
    teacher_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    qr_code: Mapped[str] = mapped_column(String(200), nullable=False)
    session_date: Mapped[date] = mapped_column(Date, server_default=func.current_date())
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    records: Mapped[list["AttendanceRecord"]] = relationship(back_populates="session")


class AttendanceMethod(str, enum.Enum):
    FACE = "face"
    QR = "qr"
    MANUAL = "manual"


class AttendanceStatus(str, enum.Enum):
    PRESENT = "present"
    LATE = "late"
    ABSENT = "absent"


class AttendanceRecord(Base):
    __tablename__ = "attendance_records"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("attendance_sessions.id"), nullable=False)
    student_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    method: Mapped[AttendanceMethod] = mapped_column(Enum(AttendanceMethod), nullable=False)
    status: Mapped[AttendanceStatus] = mapped_column(Enum(AttendanceStatus), default=AttendanceStatus.PRESENT)
    marked_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    session: Mapped[AttendanceSession] = relationship(back_populates="records")
    student: Mapped[User] = relationship("User")


class FaceProfile(Base):
    __tablename__ = "face_profiles"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True, nullable=False)
    embedding: Mapped[str] = mapped_column(Text, nullable=False)  # JSON serialized face embedding
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped[User] = relationship("User")


class Result(Base):
    __tablename__ = "results"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id"), nullable=False)
    exam_type: Mapped[str] = mapped_column(String(50), nullable=False)  # mid, final, quiz, assignment
    marks_obtained: Mapped[float] = mapped_column(Float, nullable=False)
    total_marks: Mapped[float] = mapped_column(Float, nullable=False)
    grade: Mapped[str | None] = mapped_column(String(5), nullable=True)
    grade_point: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    student: Mapped[User] = relationship("User")
    course: Mapped[Course] = relationship("Course")


class SyllabusTopic(Base):
    __tablename__ = "syllabus_topics"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    week_number: Mapped[int] = mapped_column(Integer, nullable=True)
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False)

    course: Mapped[Course] = relationship("Course")


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped[User] = relationship("User")
