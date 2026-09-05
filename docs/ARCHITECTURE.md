# CampusMind Architecture

## System Overview

```
┌─────────────┐     ┌──────────────┐     ┌──────────────┐
│   Frontend   │────▶│   Backend    │────▶│  PostgreSQL  │
│  Next.js 14  │◀────│   FastAPI    │◀────│   Database   │
│  Port 3000   │     │  Port 8000   │     │  Port 5432   │
└─────────────┘     └──────┬───────┘     └──────────────┘
                           │
                    ┌──────▼───────┐
                    │    Redis     │
                    │  Port 6379   │
                    └──────────────┘
```

## Backend Layers

```
app/
├── main.py              # App factory, lifespan, CORS, router mounting
├── core/
│   ├── config.py        # Pydantic Settings (env-based config)
│   ├── database.py      # Async SQLAlchemy engine + session
│   ├── security.py      # JWT create/decode, bcrypt hash/verify
│   └── dependencies.py  # get_current_user, require_role guards
├── models/
│   ├── user.py          # User model (student/teacher/admin)
│   └── academic.py      # Course, Enrollment, Routine, Attendance*, Result, Syllabus, Notification
├── schemas/
│   ├── auth.py          # Register/Login/Token/User response schemas
│   └── academic.py      # All academic request/response schemas
└── api/v1/endpoints/
    ├── auth.py           # Register, Login, /me
    ├── courses.py        # CRUD courses, enrollment
    ├── routines.py       # Schedule management
    ├── attendance.py     # Session creation, QR/Face marking, stats, CSV export
    ├── results.py        # Grade entry, CGPA calculation
    ├── syllabus.py       # Topic tracking
    ├── notifications.py  # User notifications
    └── assistant.py      # Bangla/English NLP → DB queries
```

## Data Flow

### Attendance Flow
```
Teacher → POST /attendance/sessions → Creates session + QR token
Student → POST /attendance/mark/qr → Validates QR + enrollment → Records present
Student → GET /attendance/course/{id}/stats → Aggregates records → Returns % + bunk calc
Anyone → GET /attendance/export/{id} → Streams CSV
```

### AI Assistant Flow
```
User message → Keyword detection (Bangla + English aliases)
  → Query type classification
  → DB query (routine/attendance/results/courses)
  → Natural language response
```

Supported query types:
- `tomorrow_class` — Joins Routine + Course + Enrollment
- `today_class` — Same with today filter
- `next_class` — Time-aware next class query
- `attendance_stats` — Aggregates across all enrolled courses
- `course_teacher` — Regex extracts course code → joins User
- `cgpa` — Groups results by course → weighted average
- `results` — Latest 5 results with grades

## Security Model

- JWT Bearer tokens (HS256, configurable expiry)
- Role-based access: `require_role(UserRole.TEACHER)` dependency
- Password hashing: bcrypt via passlib
- CORS configured for frontend origin
- Session expiry on attendance QR codes

## Database Schema

10 tables: users, courses, enrollments, routines, attendance_sessions, attendance_records, face_profiles, results, syllabus_topics, notifications

Key relationships:
- User 1:N Enrollments, Results, Notifications
- Course 1:N Routines, AttendanceSessions, Results, SyllabusTopics
- AttendanceSession 1:N AttendanceRecords
- FaceProfile 1:1 User
