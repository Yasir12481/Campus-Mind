# CampusMind

Smart Campus Management System. Pure Python stdlib + SQLite + vanilla HTML/CSS/JS. Zero frameworks.

## Run

```bash
python app.py
```

Open: http://localhost:5000

## Stack

- **Backend:** Python `http.server`, `sqlite3`, `hashlib`, `hmac`, `secrets`
- **Frontend:** Plain HTML, one CSS file, one JS file
- **Database:** SQLite (auto-created on first run)
- **Dependencies:** None. Standard library only.

## Features

- Auth (register/login/logout, session cookies, PBKDF2 password hashing)
- Role-based access (student / teacher / admin)
- Course management + enrollment
- Weekly routine timetable
- Token-based attendance (create session, mark, stats, bunk calculator)
- Results + auto grade calculation + CGPA
- Syllabus progress tracker
- Notifications
- Bangla/English rule-based academic assistant

## Structure

```
app.py          — Entire server (routing, auth, pages, API)
static/style.css — All styles
static/app.js   — Client interactivity (chat, attendance, toggles)
campusmind.db   — SQLite database (auto-created)
```
