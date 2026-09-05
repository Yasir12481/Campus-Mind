# 🎓 CampusMind — Smart Campus Management System

A full-stack campus management platform with **Face/QR Attendance**, **Bangla/English AI Assistant**, and **Academic Dashboard**.

## 🚀 Quick Start

```bash
# Clone and run
cd campusmind
docker compose up --build
```

| Service | URL |
|---------|-----|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| API Docs (Swagger) | http://localhost:8000/docs |
| PostgreSQL | localhost:5432 |
| Redis | localhost:6379 |

## 🏗️ Architecture

```
campusmind/
├── backend/          # FastAPI (Python)
│   ├── app/
│   │   ├── api/v1/endpoints/   # REST endpoints
│   │   ├── core/               # Config, DB, Security, Dependencies
│   │   ├── models/             # SQLAlchemy ORM models
│   │   ├── schemas/            # Pydantic request/response schemas
│   │   └── main.py             # App entry point
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/         # Next.js 14 + Tailwind CSS
│   ├── src/app/      # Pages (login, dashboard, teacher, assistant)
│   ├── src/lib/      # API client, Auth context
│   └── src/components/
├── docker-compose.yml
└── docs/
```

## ✨ Features

### 🔐 Authentication
- JWT-based auth with roles: Student, Teacher, Admin
- Register, Login, Protected routes

### 📸 Smart Attendance
- **QR Code**: Teacher generates session → students scan/enter code
- **Face Recognition**: MediaPipe-based face enrollment & matching (placeholder ready for expansion)
- Attendance stats, percentage, bunk calculator
- CSV export

### 🤖 AI Assistant (Bangla + English)
Rule-based NLP that queries your actual data:

| Query | Response |
|-------|----------|
| `আমার কাল কি ক্লাস?` | Tomorrow's classes from routine DB |
| `amar attendance koto?` | Overall + per-course attendance % |
| `CSE-301 er teacher ke?` | Teacher name from course DB |
| `amar cgpa koto?` | Calculated CGPA from results |
| `next class kokhon?` | Next upcoming class today |
| `amar result dekhao` | Recent results with grades |

### 📊 Academic Dashboard
- Course enrollment & management
- Class routine/schedule
- Result entry with auto grade calculation
- CGPA calculator
- Syllabus tracker with completion status
- Notifications system

## 🔌 API Endpoints (29 total)

### Auth
- `POST /api/v1/auth/register` — Create account
- `POST /api/v1/auth/login` — Get JWT token
- `GET /api/v1/auth/me` — Current user profile

### Courses
- `GET/POST /api/v1/courses/` — List/Create courses
- `POST /api/v1/courses/enroll` — Enroll student
- `GET /api/v1/courses/enrolled/me` — My enrolled courses

### Routines
- `POST /api/v1/routines/` — Create schedule entry
- `GET /api/v1/routines/me` — My weekly routine

### Attendance
- `POST /api/v1/attendance/sessions` — Teacher starts session
- `POST /api/v1/attendance/mark/qr` — Student marks via QR
- `POST /api/v1/attendance/mark/face` — Student marks via face
- `GET /api/v1/attendance/course/{id}/stats` — Stats + bunk calculator
- `GET /api/v1/attendance/export/{id}` — CSV download

### Results
- `POST /api/v1/results/` — Teacher enters marks
- `GET /api/v1/results/me/cgpa` — Student CGPA

### AI Assistant
- `POST /api/v1/assistant/chat` — Bangla/English query

### Notifications
- `GET /api/v1/notifications/me` — My notifications
- `PATCH /api/v1/notifications/{id}/read` — Mark as read

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | FastAPI, SQLAlchemy (async), PostgreSQL, Redis |
| Frontend | Next.js 14, TypeScript, Tailwind CSS |
| Auth | JWT (python-jose), bcrypt |
| Face | MediaPipe, OpenCV (extensible) |
| Deploy | Docker Compose |

## 📝 License

MIT
