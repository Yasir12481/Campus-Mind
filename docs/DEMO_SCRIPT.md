# 🎬 CampusMind — 3-Minute Demo Script

## Setup (Before Demo)
```bash
docker compose up --build
# Wait for all services to be healthy
```

Pre-create test accounts:
- Teacher: teacher@demo.com / password123
- Student: student@demo.com / password123

---

## Demo Flow (3 minutes)

### 0:00 — Introduction (15s)
> "CampusMind is a smart campus management system with face/QR attendance, a Bangla AI assistant, and a complete academic dashboard. Let me show you."

### 0:15 — Teacher Starts Attendance (30s)
1. Go to http://localhost:3000/login
2. Login as **teacher@demo.com**
3. Navigate to **Teacher Panel**
4. Select **CSE-301** course
5. Click **🚀 Start Attendance Session**
6. Show the QR code on screen

> "The teacher starts an attendance session. A unique QR code is generated that expires in 15 minutes."

### 0:45 — Student Marks Attendance (30s)
1. Open new tab → http://localhost:3000/login
2. Login as **student@demo.com**
3. Show the QR code entry (or scan)
4. Confirm attendance marked successfully

> "Students can scan the QR code or enter it manually. Face recognition is also supported as an alternative method."

### 1:15 — AI Assistant Demo (60s) ⭐ KEY MOMENT
1. Student navigates to **AI Chat**
2. Type: **"আমার কাল কি ক্লাস?"**
   - AI responds with tomorrow's schedule from DB
3. Type: **"amar attendance koto?"**
   - AI responds with actual attendance percentage
4. Type: **"CSE-301 er teacher ke?"**
   - AI responds with teacher name
5. Type: **"amar cgpa koto?"**
   - AI responds with calculated CGPA

> "The AI assistant understands both Bangla and English. It queries real database data — not canned responses. Students can ask about their classes, attendance, results, and CGPA naturally."

### 2:15 — Dashboard Overview (30s)
1. Show **Student Dashboard** with stats cards
2. Show enrolled courses list
3. Show weekly routine
4. Briefly show **CGPA calculator**

> "Everything is connected. Attendance feeds into stats, results feed into CGPA, routines feed into the AI assistant."

### 2:45 — Closing (15s)
> "CampusMind: Smart attendance, bilingual AI assistant, and unified academic management — all in one platform. Built with FastAPI, Next.js, and PostgreSQL."

---

## Backup Queries (If Time Permits)
- `next class kokhon?` → Shows next class today
- `amar result dekhao` → Shows recent results
- `আজকে কি ক্লাস আছে?` → Today's classes

## Troubleshooting
- If backend isn't responding: `docker compose logs backend`
- If frontend blank: Check browser console, ensure API_URL is correct
- If AI gives generic response: Ensure student is enrolled in courses and has attendance records
