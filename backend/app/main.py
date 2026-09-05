from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import engine, Base
from app.models.user import User  # noqa: ensure models are registered
from app.models.academic import (  # noqa
    Course, Enrollment, Routine, AttendanceSession,
    AttendanceRecord, FaceProfile, Result, SyllabusTopic, Notification
)
from app.api.v1.endpoints import auth, courses, routines, attendance, results, syllabus, notifications, assistant


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(
    title="CampusMind API",
    description="Smart Campus Management System",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth.router, prefix="/api/v1")
app.include_router(courses.router, prefix="/api/v1")
app.include_router(routines.router, prefix="/api/v1")
app.include_router(attendance.router, prefix="/api/v1")
app.include_router(results.router, prefix="/api/v1")
app.include_router(syllabus.router, prefix="/api/v1")
app.include_router(notifications.router, prefix="/api/v1")
app.include_router(assistant.router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "campusmind-backend"}
