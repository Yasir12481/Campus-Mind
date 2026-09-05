#!/usr/bin/env python3
"""CampusMind — Smart Campus Management System.
Pure Python stdlib + SQLite. Zero frameworks.
"""
import hashlib
import hmac
import json
import os
import re
import secrets
import sqlite3
import time
from datetime import date, datetime, timedelta
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse
import html as html_mod

# ─── Config ───
PORT = 5000
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'campusmind.db')
SECRET_KEY = os.environ.get('SECRET_KEY', secrets.token_hex(32))
SESSION_NAME = 'campusmind_session'
SESSION_MAX_AGE = 86400 * 7

# ─── Database ───
def get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    conn = get_db()
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'student',
        student_id TEXT,
        department TEXT,
        created_at TEXT DEFAULT (datetime('now'))
    );
    CREATE TABLE IF NOT EXISTS courses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        credits INTEGER DEFAULT 3,
        department TEXT,
        teacher_id INTEGER REFERENCES users(id),
        semester TEXT,
        created_at TEXT DEFAULT (datetime('now'))
    );
    CREATE TABLE IF NOT EXISTS enrollments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL REFERENCES users(id),
        course_id INTEGER NOT NULL REFERENCES courses(id),
        enrolled_at TEXT DEFAULT (datetime('now')),
        UNIQUE(student_id, course_id)
    );
    CREATE TABLE IF NOT EXISTS routines (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        course_id INTEGER NOT NULL REFERENCES courses(id),
        day_of_week TEXT NOT NULL,
        start_time TEXT NOT NULL,
        end_time TEXT NOT NULL,
        room TEXT NOT NULL
    );
    CREATE TABLE IF NOT EXISTS attendance_sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        course_id INTEGER NOT NULL REFERENCES courses(id),
        teacher_id INTEGER NOT NULL REFERENCES users(id),
        qr_code TEXT NOT NULL,
        session_date TEXT DEFAULT (date('now')),
        expires_at TEXT NOT NULL,
        is_active INTEGER DEFAULT 1,
        created_at TEXT DEFAULT (datetime('now'))
    );
    CREATE TABLE IF NOT EXISTS attendance_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id INTEGER NOT NULL REFERENCES attendance_sessions(id),
        student_id INTEGER NOT NULL REFERENCES users(id),
        method TEXT NOT NULL DEFAULT 'qr',
        status TEXT NOT NULL DEFAULT 'present',
        marked_at TEXT DEFAULT (datetime('now')),
        UNIQUE(session_id, student_id)
    );
    CREATE TABLE IF NOT EXISTS results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL REFERENCES users(id),
        course_id INTEGER NOT NULL REFERENCES courses(id),
        exam_type TEXT NOT NULL,
        marks_obtained REAL NOT NULL,
        total_marks REAL NOT NULL,
        grade TEXT,
        grade_point REAL,
        created_at TEXT DEFAULT (datetime('now'))
    );
    CREATE TABLE IF NOT EXISTS syllabus_topics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        course_id INTEGER NOT NULL REFERENCES courses(id),
        title TEXT NOT NULL,
        week_number INTEGER,
        is_completed INTEGER DEFAULT 0
    );
    CREATE TABLE IF NOT EXISTS notifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL REFERENCES users(id),
        title TEXT NOT NULL,
        message TEXT NOT NULL,
        is_read INTEGER DEFAULT 0,
        created_at TEXT DEFAULT (datetime('now'))
    );
    """)
    conn.commit()
    conn.close()


# ─── Auth ───
def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    h = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
    return f"{salt}:{h.hex()}"


def verify_password(password: str, stored: str) -> bool:
    salt, h = stored.split(':')
    check = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
    return hmac.compare_digest(check.hex(), h)


def create_session_token(user_id: int) -> str:
    payload = f"{user_id}:{int(time.time())}:{secrets.token_hex(8)}"
    sig = hmac.new(SECRET_KEY.encode(), payload.encode(), hashlib.sha256).hexdigest()
    return f"{payload}:{sig}"


def verify_session_token(token: str) -> int | None:
    parts = token.rsplit(':', 1)
    if len(parts) != 2:
        return None
    payload, sig = parts
    expected = hmac.new(SECRET_KEY.encode(), payload.encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(sig, expected):
        return None
    try:
        uid = int(payload.split(':')[0])
        ts = int(payload.split(':')[1])
        if time.time() - ts > SESSION_MAX_AGE:
            return None
        return uid
    except (ValueError, IndexError):
        return None


def get_current_user(handler) -> dict | None:
    cookie_header = handler.headers.get('Cookie', '')
    token = None
    for part in cookie_header.split(';'):
        part = part.strip()
        if part.startswith(f'{SESSION_NAME}='):
            token = part[len(SESSION_NAME)+1:]
            break
    if not token:
        return None
    uid = verify_session_token(token)
    if not uid:
        return None
    conn = get_db()
    row = conn.execute("SELECT * FROM users WHERE id=?", (uid,)).fetchone()
    conn.close()
    if not row:
        return None
    return dict(row)


def esc(s) -> str:
    return html_mod.escape(str(s)) if s else ''


# ─── Grade Calculator ───
def calc_grade(pct: float) -> tuple[str, float]:
    if pct >= 80: return 'A+', 4.00
    if pct >= 75: return 'A', 3.75
    if pct >= 70: return 'A-', 3.50
    if pct >= 65: return 'B+', 3.25
    if pct >= 60: return 'B', 3.00
    if pct >= 55: return 'B-', 2.75
    if pct >= 50: return 'C+', 2.50
    if pct >= 45: return 'C', 2.25
    if pct >= 40: return 'D', 2.00
    return 'F', 0.00


# ─── Layout ───
def layout(title: str, content: str, user: dict | None = None) -> str:
    nav_links = ''
    nav_user = ''
    if user:
        links = [
            ('/dashboard', 'Dashboard'),
            ('/courses', 'Courses'),
            ('/routine', 'Routine'),
            ('/attendance', 'Attendance'),
            ('/results', 'Results'),
            ('/syllabus', 'Syllabus'),
            ('/notifications', 'Notifications'),
            ('/assistant', 'Assistant'),
        ]
        if user['role'] in ('teacher', 'admin'):
            links.append(('/teacher', 'Teacher Panel'))
        nav_links = ''.join(f'<a href="{href}">{label}</a>' for href, label in links)
        nav_user = f'<span>{esc(user["name"])}</span> <span class="badge badge-blue">{esc(user["role"])}</span> <a href="/logout" class="btn btn-sm">Logout</a>'
    else:
        nav_user = '<a href="/login" class="btn btn-sm btn-primary">Login</a>'

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{esc(title)} — CampusMind</title>
    <link rel="stylesheet" href="/static/style.css">
</head>
<body>
    <nav class="nav">
        <a href="/" class="nav-brand">🎓 CampusMind</a>
        <div class="nav-links">{nav_links}</div>
        <div class="nav-user">{nav_user}</div>
    </nav>
    <div class="container">
        {content}
    </div>
    <script src="/static/app.js"></script>
</body>
</html>"""


# ─── Page Renderers ───
def page_login(error: str = '') -> str:
    err_html = f'<div class="alert alert-error">{esc(error)}</div>' if error else ''
    return layout("Login", f"""
    <div class="auth-wrap">
        <div class="auth-card">
            <h1>Welcome back</h1>
            <p class="subtitle">Sign in to CampusMind</p>
            {err_html}
            <form method="POST" action="/login">
                <div class="form-group"><label>Email</label><input type="email" name="email" required placeholder="you@university.edu"></div>
                <div class="form-group"><label>Password</label><input type="password" name="password" required placeholder="••••••••"></div>
                <button type="submit" class="btn btn-primary w-full">Sign In</button>
            </form>
            <div class="auth-footer">Don't have an account? <a href="/register">Register</a></div>
        </div>
    </div>""")


def page_register(error: str = '') -> str:
    err_html = f'<div class="alert alert-error">{esc(error)}</div>' if error else ''
    return layout("Register", f"""
    <div class="auth-wrap">
        <div class="auth-card">
            <h1>Create account</h1>
            <p class="subtitle">Join CampusMind</p>
            {err_html}
            <form method="POST" action="/register">
                <div class="form-group"><label>Full Name</label><input type="text" name="name" required></div>
                <div class="form-group"><label>Email</label><input type="email" name="email" required></div>
                <div class="form-group"><label>Password</label><input type="password" name="password" required minlength="6"></div>
                <div class="form-group"><label>Role</label>
                    <select name="role"><option value="student">Student</option><option value="teacher">Teacher</option><option value="admin">Admin</option></select>
                </div>
                <div class="form-group"><label>Student/Staff ID</label><input type="text" name="student_id" placeholder="e.g. 2403001"></div>
                <div class="form-group"><label>Department</label><input type="text" name="department" placeholder="e.g. CSE"></div>
                <button type="submit" class="btn btn-primary w-full">Register</button>
            </form>
            <div class="auth-footer">Already have an account? <a href="/login">Sign in</a></div>
        </div>
    </div>""")


def page_dashboard(user: dict) -> str:
    conn = get_db()
    uid = user['id']

    if user['role'] == 'student':
        courses = conn.execute("""
            SELECT c.* FROM courses c JOIN enrollments e ON c.id = e.course_id WHERE e.student_id=?
        """, (uid,)).fetchall()
        today = date.today().strftime('%A')
        today_classes = conn.execute("""
            SELECT r.*, c.code, c.name as course_name FROM routines r
            JOIN courses c ON r.course_id = c.id
            JOIN enrollments e ON c.id = e.course_id
            WHERE e.student_id=? AND r.day_of_week=?
            ORDER BY r.start_time
        """, (uid, today)).fetchall()
        att_stats = conn.execute("""
            SELECT COUNT(*) as total,
                   SUM(CASE WHEN ar.status='present' THEN 1 ELSE 0 END) as present
            FROM attendance_records ar
            JOIN attendance_sessions s ON ar.session_id = s.id
            WHERE ar.student_id=?
        """, (uid,)).fetchone()
        unread = conn.execute("SELECT COUNT(*) as c FROM notifications WHERE user_id=? AND is_read=0", (uid,)).fetchone()['c']
        conn.close()

        total = att_stats['total'] or 0
        present = att_stats['present'] or 0
        pct = round(present/total*100, 1) if total else 0

        courses_html = ''.join(f'<tr><td>{esc(c["code"])}</td><td>{esc(c["name"])}</td><td>{c["credits"]}</td></tr>' for c in courses) or '<tr><td colspan="3" class="text-muted">No courses enrolled yet</td></tr>'
        classes_html = ''.join(f'<tr><td>{esc(r["start_time"])}-{esc(r["end_time"])}</td><td>{esc(r["course_name"])}</td><td>{esc(r["room"])}</td></tr>' for r in today_classes) or '<tr><td colspan="3" class="text-muted">No classes today</td></tr>'

        return layout("Dashboard", f"""
        <div class="page-header"><h1>Dashboard</h1><p>Welcome back, {esc(user['name'])}</p></div>
        <div class="grid-3">
            <div class="card stat"><div class="num">{len(courses)}</div><div class="label">Courses</div></div>
            <div class="card stat"><div class="num">{pct}%</div><div class="label">Attendance</div></div>
            <div class="card stat"><div class="num">{unread}</div><div class="label">Unread Notifications</div></div>
        </div>
        <div class="grid-2">
            <div class="card"><h3>Today's Classes ({esc(today)})</h3><table><tr><th>Time</th><th>Course</th><th>Room</th></tr>{classes_html}</table></div>
            <div class="card"><h3>My Courses</h3><table><tr><th>Code</th><th>Name</th><th>Cr</th></tr>{courses_html}</table></div>
        </div>""", user)

    elif user['role'] in ('teacher', 'admin'):
        courses = conn.execute("SELECT * FROM courses WHERE teacher_id=?", (uid,)).fetchall()
        total_students = conn.execute("SELECT COUNT(*) as c FROM users WHERE role='student'").fetchone()['c']
        conn.close()
        courses_html = ''.join(f'<tr><td>{esc(c["code"])}</td><td>{esc(c["name"])}</td><td>{esc(c["semester"] or "-")}</td></tr>' for c in courses) or '<tr><td colspan="3" class="text-muted">No courses assigned</td></tr>'

        return layout("Dashboard", f"""
        <div class="page-header"><h1>Dashboard</h1><p>Welcome, {esc(user['name'])}</p></div>
        <div class="grid-3">
            <div class="card stat"><div class="num">{len(courses)}</div><div class="label">My Courses</div></div>
            <div class="card stat"><div class="num">{total_students}</div><div class="label">Students</div></div>
            <div class="card stat"><div class="num">{date.today().strftime('%d %b')}</div><div class="label">Today</div></div>
        </div>
        <div class="card"><h3>My Courses</h3><table><tr><th>Code</th><th>Name</th><th>Semester</th></tr>{courses_html}</table></div>""", user)

    conn.close()
    return layout("Dashboard", "<div class='page-header'><h1>Dashboard</h1></div>", user)


def page_courses(user: dict) -> str:
    conn = get_db()
    courses = conn.execute("SELECT c.*, u.name as teacher_name FROM courses c LEFT JOIN users u ON c.teacher_id=u.id").fetchall()
    if user['role'] == 'student':
        my_enrollments = [r['course_id'] for r in conn.execute("SELECT course_id FROM enrollments WHERE student_id=?", (user['id'],)).fetchall()]
    else:
        my_enrollments = []
    conn.close()

    rows = ''
    for c in courses:
        enrolled = c['id'] in my_enrollments
        status = '<span class="badge badge-green">Enrolled</span>' if enrolled else f'<a href="/courses/enroll/{c["id"]}" class="btn btn-sm btn-primary">Enroll</a>'
        if user['role'] != 'student':
            status = f'<span class="badge badge-blue">{esc(c["teacher_name"] or "Unassigned")}</span>'
        rows += f'<tr><td>{esc(c["code"])}</td><td>{esc(c["name"])}</td><td>{c["credits"]}</td><td>{esc(c["department"] or "-")}</td><td>{status}</td></tr>'

    create_form = ''
    if user['role'] in ('teacher', 'admin'):
        create_form = f"""
        <div class="card"><h3>Add Course</h3>
        <form method="POST" action="/courses/create" class="grid-2">
            <div class="form-group"><label>Code</label><input name="code" required placeholder="CSE-101"></div>
            <div class="form-group"><label>Name</label><input name="name" required placeholder="Data Structures"></div>
            <div class="form-group"><label>Credits</label><input name="credits" type="number" value="3"></div>
            <div class="form-group"><label>Department</label><input name="department" placeholder="CSE"></div>
            <div class="form-group"><label>Semester</label><input name="semester" placeholder="1st"></div>
            <div class="form-group"><button type="submit" class="btn btn-primary">Add Course</button></div>
        </form></div>"""

    return layout("Courses", f"""
    <div class="page-header"><h1>Courses</h1><p>{len(courses)} courses available</p></div>
    <div class="card"><table><tr><th>Code</th><th>Name</th><th>Credits</th><th>Dept</th><th>Action</th></tr>{rows or '<tr><td colspan="5" class="text-muted">No courses yet</td></tr>'}</table></div>
    {create_form}""", user)


def page_routine(user: dict) -> str:
    conn = get_db()
    days = ['Saturday', 'Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']

    if user['role'] == 'student':
        routines = conn.execute("""
            SELECT r.*, c.code, c.name as course_name FROM routines r
            JOIN courses c ON r.course_id = c.id
            JOIN enrollments e ON c.id = e.course_id
            WHERE e.student_id=?
        """, (user['id'],)).fetchall()
    else:
        routines = conn.execute("""
            SELECT r.*, c.code, c.name as course_name FROM routines r
            JOIN courses c ON r.course_id = c.id
            WHERE c.teacher_id=? OR ?='admin'
        """, (user['id'], user['role'])).fetchall()
    conn.close()

    timetable = {d: [] for d in days}
    for r in routines:
        if r['day_of_week'] in timetable:
            timetable[r['day_of_week']].append(r)

    table_rows = ''
    for day in days:
        slots = timetable[day]
        slots_html = '<br>'.join(f'{esc(s["start_time"])}-{esc(s["end_time"])} | {esc(s["course_name"])} | {esc(s["room"])}' for s in sorted(slots, key=lambda x: x['start_time'])) or '<span class="text-muted">—</span>'
        table_rows += f'<tr><td><strong>{day}</strong></td><td>{slots_html}</td></tr>'

    add_form = ''
    if user['role'] in ('teacher', 'admin'):
        conn = get_db()
        if user['role'] == 'admin':
            my_courses = conn.execute("SELECT * FROM courses").fetchall()
        else:
            my_courses = conn.execute("SELECT * FROM courses WHERE teacher_id=?", (user['id'],)).fetchall()
        conn.close()
        opts = ''.join(f'<option value="{c["id"]}">{esc(c["code"])} - {esc(c["name"])}</option>' for c in my_courses)
        day_opts = ''.join(f'<option value="{d}">{d}</option>' for d in days)
        add_form = f"""
        <div class="card"><h3>Add Routine Entry</h3>
        <form method="POST" action="/routine/create">
            <div class="grid-2">
                <div class="form-group"><label>Course</label><select name="course_id">{opts}</select></div>
                <div class="form-group"><label>Day</label><select name="day_of_week">{day_opts}</select></div>
                <div class="form-group"><label>Start</label><input type="time" name="start_time" required></div>
                <div class="form-group"><label>End</label><input type="time" name="end_time" required></div>
                <div class="form-group"><label>Room</label><input name="room" required placeholder="Room 101"></div>
                <div class="form-group"><button type="submit" class="btn btn-primary">Add</button></div>
            </div>
        </form></div>"""

    return layout("Routine", f"""
    <div class="page-header"><h1>Weekly Routine</h1></div>
    <div class="card"><table><tr><th style="width:120px">Day</th><th>Classes</th></tr>{table_rows}</table></div>
    {add_form}""", user)


def page_attendance(user: dict) -> str:
    conn = get_db()

    if user['role'] == 'student':
        records = conn.execute("""
            SELECT ar.*, s.session_date, c.code, c.name as course_name
            FROM attendance_records ar
            JOIN attendance_sessions s ON ar.session_id = s.id
            JOIN courses c ON s.course_id = c.id
            WHERE ar.student_id=?
            ORDER BY ar.marked_at DESC LIMIT 50
        """, (user['id'],)).fetchall()
        conn.close()

        rows = ''.join(f'<tr><td>{esc(r["session_date"])}</td><td>{esc(r["course_name"])}</td><td><span class="badge badge-green">{esc(r["status"])}</span></td><td>{esc(r["method"])}</td></tr>' for r in records) or '<tr><td colspan="4" class="text-muted">No attendance records</td></tr>'

        return layout("Attendance", f"""
        <div class="page-header"><h1>Attendance</h1></div>
        <div class="card">
            <h3>Mark Attendance</h3>
            <form id="attendanceForm">
                <div class="grid-2">
                    <div class="form-group"><label>Session ID</label><input name="session_id" required placeholder="Enter session ID"></div>
                    <div class="form-group"><label>Code</label><input name="code" required placeholder="Enter attendance code"></div>
                </div>
                <button type="submit" class="btn btn-primary">Mark Present</button>
            </form>
            <div id="attendanceResult" class="mt-2"></div>
        </div>
        <div class="card"><h3>History</h3><table><tr><th>Date</th><th>Course</th><th>Status</th><th>Method</th></tr>{rows}</table></div>""", user)

    else:
        # Teacher view
        sessions = conn.execute("""
            SELECT s.*, c.code FROM attendance_sessions s
            JOIN courses c ON s.course_id = c.id
            WHERE s.teacher_id=?
            ORDER BY s.created_at DESC LIMIT 20
        """, (user['id'],)).fetchall()
        courses = conn.execute("SELECT * FROM courses WHERE teacher_id=?", (user['id'],)).fetchall()
        conn.close()

        sess_rows = ''
        for s in sessions:
            status = '<span class="badge badge-green">Active</span>' if s['is_active'] else '<span class="badge badge-gray">Closed</span>'
            sess_rows += f'<tr><td>#{s["id"]}</td><td>{esc(s["code"])}</td><td><code>{esc(s["qr_code"])}</code></td><td>{esc(s["session_date"])}</td><td>{status}</td></tr>'

        course_opts = ''.join(f'<option value="{c["id"]}">{esc(c["code"])}</option>' for c in courses)

        return layout("Attendance", f"""
        <div class="page-header"><h1>Attendance</h1><p>Manage attendance sessions</p></div>
        <div class="card">
            <h3>Create Session</h3>
            <form method="POST" action="/attendance/create">
                <div class="grid-3">
                    <div class="form-group"><label>Course</label><select name="course_id">{course_opts}</select></div>
                    <div class="form-group"><label>Duration (min)</label><input name="duration" type="number" value="10" min="1" max="60"></div>
                    <div class="form-group"><button type="submit" class="btn btn-primary">Start Session</button></div>
                </div>
            </form>
        </div>
        <div class="card"><h3>Sessions</h3><table><tr><th>ID</th><th>Course</th><th>Code</th><th>Date</th><th>Status</th></tr>{sess_rows or '<tr><td colspan="5" class="text-muted">No sessions yet</td></tr>'}</table></div>""", user)


def page_results(user: dict) -> str:
    conn = get_db()

    if user['role'] == 'student':
        results = conn.execute("""
            SELECT r.*, c.code, c.name as course_name FROM results r
            JOIN courses c ON r.course_id = c.id
            WHERE r.student_id=?
            ORDER BY r.created_at DESC
        """, (user['id'],)).fetchall()
        conn.close()

        # CGPA calc
        total_gp = sum(r['grade_point'] * next((c['credits'] for c in [{'id': r['course_id'], 'credits': 3}]), 3) for r in results if r['grade_point'] is not None)
        total_cr = len(results) * 3
        cgpa = round(total_gp / total_cr, 2) if total_cr else 0

        rows = ''.join(f'<tr><td>{esc(r["code"])}</td><td>{esc(r["exam_type"])}</td><td>{r["marks_obtained"]}/{r["total_marks"]}</td><td><span class="badge badge-blue">{esc(r["grade"])}</span></td><td>{r["grade_point"]:.2f}</td></tr>' for r in results) or '<tr><td colspan="5" class="text-muted">No results yet</td></tr>'

        return layout("Results", f"""
        <div class="page-header"><h1>Results</h1></div>
        <div class="grid-3">
            <div class="card stat"><div class="num">{len(results)}</div><div class="label">Total Results</div></div>
            <div class="card stat"><div class="num">{cgpa:.2f}</div><div class="label">CGPA</div></div>
            <div class="card stat"><div class="num">{date.today().year}</div><div class="label">Year</div></div>
        </div>
        <div class="card"><table><tr><th>Course</th><th>Exam</th><th>Marks</th><th>Grade</th><th>GP</th></tr>{rows}</table></div>""", user)

    else:
        results = conn.execute("""
            SELECT r.*, c.code, u.name as student_name FROM results r
            JOIN courses c ON r.course_id = c.id
            JOIN users u ON r.student_id = u.id
            ORDER BY r.created_at DESC LIMIT 50
        """).fetchall()
        conn.close()
        rows = ''.join(f'<tr><td>{esc(r["student_name"])}</td><td>{esc(r["code"])}</td><td>{esc(r["exam_type"])}</td><td>{r["marks_obtained"]}/{r["total_marks"]}</td><td>{esc(r["grade"])}</td></tr>' for r in results) or '<tr><td colspan="5" class="text-muted">No results</td></tr>'
        return layout("Results", f"""
        <div class="page-header"><h1>Results</h1><p>All student results</p></div>
        <div class="card"><table><tr><th>Student</th><th>Course</th><th>Exam</th><th>Marks</th><th>Grade</th></tr>{rows}</table></div>""", user)


def page_syllabus(user: dict) -> str:
    conn = get_db()

    if user['role'] == 'student':
        courses = conn.execute("""
            SELECT c.* FROM courses c JOIN enrollments e ON c.id = e.course_id WHERE e.student_id=?
        """, (user['id'],)).fetchall()
    else:
        courses = conn.execute("SELECT * FROM courses").fetchall()

    all_topics = {}
    for c in courses:
        topics = conn.execute("SELECT * FROM syllabus_topics WHERE course_id=? ORDER BY week_number", (c['id'],)).fetchall()
        all_topics[c['id']] = {'course': c, 'topics': topics}
    conn.close()

    sections = ''
    for cid, data in all_topics.items():
        c = data['course']
        topics = data['topics']
        completed = sum(1 for t in topics if t['is_completed'])
        total = len(topics)
        pct = round(completed/total*100) if total else 0

        topic_rows = ''
        for t in topics:
            check = '✓' if t['is_completed'] else '○'
            cls = 'badge-green' if t['is_completed'] else 'badge-gray'
            toggle_btn = ''
            if user['role'] in ('teacher', 'admin'):
                toggle_btn = f'<button class="btn btn-sm syllabus-toggle" data-id="{t["id"]}">Toggle</button>'
            topic_rows += f'<tr><td>{check}</td><td>Week {t["week_number"] or "-"}</td><td>{esc(t["title"])}</td><td><span class="badge {cls}">{"Done" if t["is_completed"] else "Pending"}</span></td><td>{toggle_btn}</td></tr>'

        sections += f"""
        <div class="card">
            <div class="flex-between mb-2">
                <h3>{esc(c['code'])} — {esc(c['name'])}</h3>
                <span class="badge badge-blue">{pct}% complete</span>
            </div>
            <table><tr><th></th><th>Week</th><th>Topic</th><th>Status</th><th></th></tr>{topic_rows or '<tr><td colspan="5" class="text-muted">No topics added</td></tr>'}</table>
        </div>"""

    add_form = ''
    if user['role'] in ('teacher', 'admin'):
        course_opts = ''.join(f'<option value="{cid}">{esc(d["course"]["code"])}</option>' for cid, d in all_topics.items())
        add_form = f"""
        <div class="card"><h3>Add Topic</h3>
        <form method="POST" action="/syllabus/create">
            <div class="grid-3">
                <div class="form-group"><label>Course</label><select name="course_id">{course_opts}</select></div>
                <div class="form-group"><label>Title</label><input name="title" required placeholder="Topic name"></div>
                <div class="form-group"><label>Week #</label><input name="week_number" type="number" min="1" value="1"></div>
            </div>
            <button type="submit" class="btn btn-primary">Add Topic</button>
        </form></div>"""

    return layout("Syllabus", f"""
    <div class="page-header"><h1>Syllabus Tracker</h1><p>Track course syllabus progress</p></div>
    {sections or '<div class="empty-state"><div class="icon">📚</div><p>No courses found</p></div>'}
    {add_form}""", user)


def page_notifications(user: dict) -> str:
    conn = get_db()
    notifs = conn.execute("SELECT * FROM notifications WHERE user_id=? ORDER BY created_at DESC", (user['id'],)).fetchall()
    conn.close()

    items = ''
    for n in notifs:
        read_cls = '' if n['is_read'] else 'style="border-left:3px solid var(--accent)"'
        read_btn = '' if n['is_read'] else f'<button class="btn btn-sm notif-read" data-id="{n["id"]}">Mark Read</button>'
        items += f'<div class="card" {read_cls}><div class="flex-between"><div><strong>{esc(n["title"])}</strong><p class="text-sm text-muted">{esc(n["message"])}</p><span class="text-sm text-muted">{esc(n["created_at"])}</span></div>{read_btn}</div></div>'

    return layout("Notifications", f"""
    <div class="page-header"><h1>Notifications</h1></div>
    {items or '<div class="empty-state"><div class="icon">🔔</div><p>No notifications</p></div>'}""", user)


def page_assistant(user: dict) -> str:
    return layout("Assistant", f"""
    <div class="page-header"><h1>AI Assistant</h1><p>Ask in Bangla or English</p></div>
    <div class="card">
        <div class="chat-container">
            <div class="chat-messages" id="chatMessages">
                <div class="chat-msg bot">Hello! Try asking:<br>• "amar kal ki class?"<br>• "amar attendance koto?"<br>• "CSE-301 er teacher ke?"<br>• "amar cgpa koto?"</div>
            </div>
            <div class="chat-input-row">
                <input id="chatInput" placeholder="Ask me anything..." autocomplete="off">
                <button id="chatSend" class="btn btn-primary">Send</button>
            </div>
        </div>
    </div>""", user)


def page_teacher(user: dict) -> str:
    conn = get_db()
    courses = conn.execute("SELECT * FROM courses WHERE teacher_id=?", (user['id'],)).fetchall()
    students = conn.execute("SELECT * FROM users WHERE role='student'").fetchall()
    conn.close()

    course_opts = ''.join(f'<option value="{c["id"]}">{esc(c["code"])} - {esc(c["name"])}</option>' for c in courses)
    student_opts = ''.join(f'<option value="{s["id"]}">{esc(s["name"])} ({esc(s["student_id"] or s["email"])})</option>' for s in students)

    return layout("Teacher Panel", f"""
    <div class="page-header"><h1>Teacher Panel</h1><p>Enter results and manage syllabus</p></div>
    <div class="card">
        <h3>Enter Result</h3>
        <form method="POST" action="/teacher/result">
            <div class="grid-3">
                <div class="form-group"><label>Student</label><select name="student_id">{student_opts}</select></div>
                <div class="form-group"><label>Course</label><select name="course_id">{course_opts}</select></div>
                <div class="form-group"><label>Exam Type</label>
                    <select name="exam_type"><option>Midterm</option><option>Final</option><option>Quiz</option><option>Lab</option><option>Assignment</option></select>
                </div>
                <div class="form-group"><label>Marks</label><input name="marks_obtained" type="number" required step="0.5"></div>
                <div class="form-group"><label>Total Marks</label><input name="total_marks" type="number" value="100" required></div>
                <div class="form-group"><button type="submit" class="btn btn-primary">Submit Result</button></div>
            </div>
        </form>
    </div>
    <div class="card">
        <h3>Add Syllabus Topic</h3>
        <form method="POST" action="/syllabus/create">
            <div class="grid-3">
                <div class="form-group"><label>Course</label><select name="course_id">{course_opts}</select></div>
                <div class="form-group"><label>Title</label><input name="title" required></div>
                <div class="form-group"><label>Week</label><input name="week_number" type="number" value="1" min="1"></div>
            </div>
            <button type="submit" class="btn btn-primary">Add Topic</button>
        </form>
    </div>""", user)


# ─── Assistant Logic ───
def assistant_reply(user: dict, message: str) -> str:
    msg = message.lower().strip()
    conn = get_db()
    uid = user['id']
    today = date.today()
    today_name = today.strftime('%A')
    tomorrow_name = (today + timedelta(days=1)).strftime('%A')

    # Today's classes
    if any(k in msg for k in ['aj', 'ajker', 'আজ', 'today']):
        rows = conn.execute("""
            SELECT r.*, c.code, c.name as cname FROM routines r
            JOIN courses c ON r.course_id=c.id
            JOIN enrollments e ON c.id=e.course_id
            WHERE e.student_id=? AND r.day_of_week=?
            ORDER BY r.start_time
        """, (uid, today_name)).fetchall()
        conn.close()
        if not rows:
            return "আজ তোমার কোনো ক্লাস নেই। / No classes today! 🎉"
        lines = [f"{r['start_time']}-{r['end_time']} | {r['cname']} | {r['room']}" for r in rows]
        return f"আজকের ক্লাস ({today_name}):\n" + "\n".join(lines)

    # Tomorrow's classes
    if any(k in msg for k in ['kal', 'আগামী', 'কাল', 'tomorrow']):
        rows = conn.execute("""
            SELECT r.*, c.code, c.name as cname FROM routines r
            JOIN courses c ON r.course_id=c.id
            JOIN enrollments e ON c.id=e.course_id
            WHERE e.student_id=? AND r.day_of_week=?
            ORDER BY r.start_time
        """, (uid, tomorrow_name)).fetchall()
        conn.close()
        if not rows:
            return "কাল কোনো ক্লাস নেই! / No classes tomorrow! 🎉"
        lines = [f"{r['start_time']}-{r['end_time']} | {r['cname']} | {r['room']}" for r in rows]
        return f"কালকের ক্লাস ({tomorrow_name}):\n" + "\n".join(lines)

    # Attendance
    if any(k in msg for k in ['attendance', 'উপস্থিতি', 'hajir', 'হাজির']):
        stats = conn.execute("""
            SELECT COUNT(*) as total, SUM(CASE WHEN status='present' THEN 1 ELSE 0 END) as present
            FROM attendance_records WHERE student_id=?
        """, (uid,)).fetchone()
        conn.close()
        total = stats['total'] or 0
        present = stats['present'] or 0
        if total == 0:
            return "তোমার কোনো অ্যাটেন্ডেন্স রেকর্ড নেই। / No attendance records found."
        pct = round(present/total*100, 1)
        bunk = max(0, int((present - 0.75*total) / 0.75))
        return f"তোমার অ্যাটেন্ডেন্স: {present}/{total} ({pct}%)\n75% এর উপরে থাকতে আরো {bunk} টা ক্লাস মিস করতে পারবে।"

    # CGPA
    if any(k in msg for k in ['cgpa', 'সিজিপিএ', 'gpa']):
        results = conn.execute("SELECT grade_point FROM results WHERE student_id=? AND grade_point IS NOT NULL", (uid,)).fetchall()
        conn.close()
        if not results:
            return "তোমার কোনো রেজাল্ট নেই। / No results found."
        cgpa = sum(r['grade_point'] for r in results) / len(results)
        return f"তোমার সিজিপিএ: {cgpa:.2f}"

    # Results
    if any(k in msg for k in ['result', 'রেজাল্ট', 'marks', 'মার্কস']):
        results = conn.execute("""
            SELECT r.*, c.code FROM results r JOIN courses c ON r.course_id=c.id WHERE r.student_id=?
        """, (uid,)).fetchall()
        conn.close()
        if not results:
            return "কোনো রেজাল্ট পাওয়া যায়নি। / No results found."
        lines = [f"{r['code']} | {r['exam_type']} | {r['marks_obtained']}/{r['total_marks']} | {r['grade']}" for r in results]
        return "তোমার রেজাল্ট:\n" + "\n".join(lines)

    # Course teacher
    teacher_match = re.search(r'(\w+-\d+)\s*(er|এর)?\s*(teacher|শিক্ষক)', msg)
    if teacher_match:
        code = teacher_match.group(1).upper()
        row = conn.execute("""
            SELECT c.code, u.name FROM courses c JOIN users u ON c.teacher_id=u.id WHERE c.code=?
        """, (code,)).fetchone()
        conn.close()
        if row:
            return f"{row['code']} এর শিক্ষক: {row['name']}"
        return f"{code} কোর্স পাওয়া যায়নি।"
    teacher_match = re.search(r'(?:শিক্ষক|teacher)\s*কে\s*(\w+-\d+)', msg)
    if teacher_match:
        code = teacher_match.group(1).upper()
        row = conn.execute("SELECT c.code, u.name FROM courses c JOIN users u ON c.teacher_id=u.id WHERE c.code=?", (code,)).fetchone()
        conn.close()
        if row:
            return f"{row['code']} এর শিক্ষক: {row['name']}"
        return f"{code} কোর্স পাওয়া যায়নি।"
    conn.close()

    return """আমি এসব সাহায্য করতে পারি:\n• "amar kal ki class?" — কালকের ক্লাস\n• "amar aj ki class?" — আজকের ক্লাস\n• "amar attendance koto?" — অ্যাটেন্ডেন্স\n• "amar cgpa koto?" — সিজিপিএ\n• "amar result dekhao" — রেজাল্ট\n• "CSE-301 er teacher ke?" — কোর্স টিচার"""


# ─── HTTP Handler ───
class Handler(BaseHTTPRequestHandler):

    def send_html(self, html: str, status: int = 200):
        self.send_response(status)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html.encode())

    def send_json(self, data: dict, status: int = 200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def send_redirect(self, path: str, cookie: str = ''):
        self.send_response(302)
        if cookie:
            self.send_header('Set-Cookie', cookie)
        self.send_header('Location', path)
        self.end_headers()

    def read_body(self) -> dict:
        length = int(self.headers.get('Content-Length', 0))
        if length == 0:
            return {}
        raw = self.rfile.read(length).decode()
        ct = self.headers.get('Content-Type', '')
        if 'application/json' in ct:
            return json.loads(raw)
        return {k: v[0] for k, v in parse_qs(raw).items()}

    def get_user(self) -> dict | None:
        return get_current_user(self)

    def require_auth(self) -> dict | None:
        user = self.get_user()
        if not user:
            self.send_redirect('/login')
            return None
        return user

    # ── GET Routes ──
    def do_GET(self):
        path = urlparse(self.path).path

        if path.startswith('/static/'):
            self.serve_static(path)
            return

        if path == '/login':
            self.send_html(page_login())
            return
        if path == '/register':
            self.send_html(page_register())
            return
        if path == '/logout':
            self.send_redirect('/login', f'{SESSION_NAME}=; Max-Age=0; Path=/')
            return

        # Course enroll shortcut
        if path.startswith('/courses/enroll/'):
            user = self.require_auth()
            if not user:
                return
            cid = path.split('/')[-1]
            try:
                conn = get_db()
                conn.execute("INSERT OR IGNORE INTO enrollments (student_id, course_id) VALUES (?,?)", (user['id'], int(cid)))
                conn.commit()
                conn.close()
            except Exception:
                pass
            self.send_redirect('/courses')
            return

        user = self.require_auth()
        if not user:
            return

        routes = {
            '/': lambda: self.send_redirect('/dashboard'),
            '/dashboard': lambda: self.send_html(page_dashboard(user)),
            '/courses': lambda: self.send_html(page_courses(user)),
            '/routine': lambda: self.send_html(page_routine(user)),
            '/attendance': lambda: self.send_html(page_attendance(user)),
            '/results': lambda: self.send_html(page_results(user)),
            '/syllabus': lambda: self.send_html(page_syllabus(user)),
            '/notifications': lambda: self.send_html(page_notifications(user)),
            '/assistant': lambda: self.send_html(page_assistant(user)),
            '/teacher': lambda: self.send_html(page_teacher(user)) if user['role'] in ('teacher', 'admin') else self.send_html(page_dashboard(user)),
        }

        if path in routes:
            routes[path]()
            return

        self.send_html(layout("404", "<div class='empty-state'><div class='icon'>404</div><p>Page not found</p></div>", user), 404)

    # ── POST Routes ──
    def do_POST(self):
        path = urlparse(self.path).path
        body = self.read_body()

        if path.startswith('/api/'):
            self.handle_api(path, body)
            return

        if path == '/login':
            self.handle_login(body)
        elif path == '/register':
            self.handle_register(body)
        elif path == '/courses/create':
            self.handle_course_create(body)
        elif path == '/routine/create':
            self.handle_routine_create(body)
        elif path == '/attendance/create':
            self.handle_attendance_create(body)
        elif path == '/teacher/result':
            self.handle_result_submit(body)
        elif path == '/syllabus/create':
            self.handle_syllabus_create(body)
        else:
            self.send_redirect('/')

    # ── API Routes ──
    def handle_api(self, path: str, body: dict):
        user = self.get_user()
        if not user:
            self.send_json({'error': 'Unauthorized'}, 401)
            return

        if path == '/api/assistant/chat':
            msg = body.get('message', '')
            reply = assistant_reply(user, msg)
            self.send_json({'reply': reply, 'type': 'assistant'})
            return

        if path == '/api/attendance/mark':
            session_id = body.get('session_id', '')
            code = body.get('code', '')
            conn = get_db()
            session = conn.execute("SELECT * FROM attendance_sessions WHERE id=?", (session_id,)).fetchone()
            if not session:
                self.send_json({'success': False, 'message': 'Session not found'}, 404)
                conn.close()
                return
            if session['qr_code'] != code:
                self.send_json({'success': False, 'message': 'Invalid code'}, 400)
                conn.close()
                return
            if not session['is_active']:
                self.send_json({'success': False, 'message': 'Session is closed'}, 400)
                conn.close()
                return
            if datetime.fromisoformat(session['expires_at']) < datetime.now():
                self.send_json({'success': False, 'message': 'Session expired'}, 400)
                conn.close()
                return
            enrolled = conn.execute("SELECT id FROM enrollments WHERE student_id=? AND course_id=?", (user['id'], session['course_id'])).fetchone()
            if not enrolled:
                self.send_json({'success': False, 'message': 'Not enrolled in this course'}, 403)
                conn.close()
                return
            try:
                conn.execute("INSERT INTO attendance_records (session_id, student_id, method, status) VALUES (?,?,?,?)",
                           (session['id'], user['id'], 'qr', 'present'))
                conn.commit()
                self.send_json({'success': True, 'message': 'Attendance marked! ✓'})
            except sqlite3.IntegrityError:
                self.send_json({'success': False, 'message': 'Already marked attendance for this session'})
            conn.close()
            return

        if path.startswith('/api/syllabus/') and path.endswith('/toggle'):
            tid = path.split('/')[3]
            conn = get_db()
            conn.execute("UPDATE syllabus_topics SET is_completed = 1 - is_completed WHERE id=?", (tid,))
            conn.commit()
            conn.close()
            self.send_json({'success': True})
            return

        if path.startswith('/api/notifications/') and path.endswith('/read'):
            nid = path.split('/')[3]
            conn = get_db()
            conn.execute("UPDATE notifications SET is_read=1 WHERE id=? AND user_id=?", (nid, user['id']))
            conn.commit()
            conn.close()
            self.send_json({'success': True})
            return

        self.send_json({'error': 'Not found'}, 404)

    # ── Auth Handlers ──
    def handle_login(self, body: dict):
        email = body.get('email', '').strip()
        password = body.get('password', '')
        conn = get_db()
        row = conn.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
        conn.close()

        if not row or not verify_password(password, row['password_hash']):
            self.send_html(page_login("Invalid email or password"), 401)
            return

        token = create_session_token(row['id'])
        self.send_redirect('/dashboard', f'{SESSION_NAME}={token}; Path=/; HttpOnly; Max-Age={SESSION_MAX_AGE}')

    def handle_register(self, body: dict):
        name = body.get('name', '').strip()
        email = body.get('email', '').strip()
        password = body.get('password', '')
        role = body.get('role', 'student')
        student_id = body.get('student_id', '')
        department = body.get('department', '')

        if not name or not email or not password:
            self.send_html(page_register("All fields required"), 400)
            return
        if len(password) < 6:
            self.send_html(page_register("Password must be at least 6 characters"), 400)
            return

        conn = get_db()
        existing = conn.execute("SELECT id FROM users WHERE email=?", (email,)).fetchone()
        if existing:
            self.send_html(page_register("Email already registered"), 409)
            conn.close()
            return

        conn.execute("INSERT INTO users (name, email, password_hash, role, student_id, department) VALUES (?,?,?,?,?,?)",
                    (name, email, hash_password(password), role, student_id, department))
        conn.commit()
        row = conn.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
        conn.close()

        token = create_session_token(row['id'])
        self.send_redirect('/dashboard', f'{SESSION_NAME}={token}; Path=/; HttpOnly; Max-Age={SESSION_MAX_AGE}')

    # ── Form Handlers ──
    def handle_course_create(self, body: dict):
        user = self.require_auth()
        if not user or user['role'] not in ('teacher', 'admin'):
            self.send_redirect('/courses')
            return
        conn = get_db()
        try:
            conn.execute("INSERT INTO courses (code, name, credits, department, teacher_id, semester) VALUES (?,?,?,?,?,?)",
                        (body.get('code',''), body.get('name',''), int(body.get('credits',3)),
                         body.get('department',''), user['id'] if user['role']=='teacher' else None,
                         body.get('semester','')))
            conn.commit()
        except sqlite3.IntegrityError:
            pass
        conn.close()
        self.send_redirect('/courses')

    def handle_routine_create(self, body: dict):
        user = self.require_auth()
        if not user:
            return
        conn = get_db()
        conn.execute("INSERT INTO routines (course_id, day_of_week, start_time, end_time, room) VALUES (?,?,?,?,?)",
                    (int(body.get('course_id',0)), body.get('day_of_week',''), body.get('start_time',''),
                     body.get('end_time',''), body.get('room','')))
        conn.commit()
        conn.close()
        self.send_redirect('/routine')

    def handle_attendance_create(self, body: dict):
        user = self.require_auth()
        if not user or user['role'] not in ('teacher', 'admin'):
            self.send_redirect('/attendance')
            return
        duration = int(body.get('duration', 10))
        code = secrets.token_hex(6)
        expires = (datetime.now() + timedelta(minutes=duration)).isoformat()
        conn = get_db()
        conn.execute("INSERT INTO attendance_sessions (course_id, teacher_id, qr_code, expires_at) VALUES (?,?,?,?)",
                    (int(body.get('course_id',0)), user['id'], code, expires))
        conn.commit()
        conn.close()
        self.send_redirect('/attendance')

    def handle_result_submit(self, body: dict):
        user = self.require_auth()
        if not user or user['role'] not in ('teacher', 'admin'):
            self.send_redirect('/results')
            return
        marks = float(body.get('marks_obtained', 0))
        total = float(body.get('total_marks', 100))
        pct = (marks/total)*100 if total else 0
        grade, gp = calc_grade(pct)
        conn = get_db()
        conn.execute("INSERT INTO results (student_id, course_id, exam_type, marks_obtained, total_marks, grade, grade_point) VALUES (?,?,?,?,?,?,?)",
                    (int(body.get('student_id',0)), int(body.get('course_id',0)), body.get('exam_type',''),
                     marks, total, grade, gp))
        conn.commit()
        conn.close()
        self.send_redirect('/teacher')

    def handle_syllabus_create(self, body: dict):
        user = self.require_auth()
        if not user:
            return
        conn = get_db()
        conn.execute("INSERT INTO syllabus_topics (course_id, title, week_number) VALUES (?,?,?)",
                    (int(body.get('course_id',0)), body.get('title',''), int(body.get('week_number',1))))
        conn.commit()
        conn.close()
        self.send_redirect('/syllabus')

    # ── Static Files ──
    def serve_static(self, path: str):
        base = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(base, path.lstrip('/'))
        if not os.path.isfile(file_path):
            self.send_response(404)
            self.end_headers()
            return
        ext = os.path.splitext(file_path)[1]
        ct = {'.css': 'text/css', '.js': 'application/javascript', '.png': 'image/png', '.ico': 'image/x-icon'}.get(ext, 'application/octet-stream')
        with open(file_path, 'rb') as f:
            data = f.read()
        self.send_response(200)
        self.send_header('Content-Type', ct)
        self.send_header('Content-Length', len(data))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, format, *args):
        pass


# ─── Main ───
if __name__ == '__main__':
    init_db()
    print(f"🎓 CampusMind running at http://localhost:{PORT}")
    server = HTTPServer(('0.0.0.0', PORT), Handler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down.")
        server.shutdown()
