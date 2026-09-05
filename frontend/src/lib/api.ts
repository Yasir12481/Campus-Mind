const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json", ...options.headers },
    ...options,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || `Request failed: ${res.status}`);
  }
  if (res.status === 204) return undefined as T;
  return res.json();
}

function authHeaders(token: string): Record<string, string> {
  return { Authorization: `Bearer ${token}` };
}

// ── Auth ──
export const authApi = {
  register: (data: { name: string; email: string; password: string; role: string }) =>
    request<{ access_token: string; user: { id: number; name: string; email: string; role: string } }>("/auth/register", {
      method: "POST",
      body: JSON.stringify(data),
    }),
  login: (data: { email: string; password: string }) =>
    request<{ access_token: string; user: { id: number; name: string; email: string; role: string } }>("/auth/login", {
      method: "POST",
      body: JSON.stringify(data),
    }),
};

// ── Courses ──
export const coursesApi = {
  list: (token: string) =>
    request<Array<{ id: number; code: string; name: string; credits: number; department: string | null; semester: string | null }>>("/courses/", {
      headers: authHeaders(token),
    }),
  catalog: (token: string) =>
    request<Array<{ id: number; code: string; name: string; credits: number; department: string | null; semester: string | null }>>("/courses/catalog", {
      headers: authHeaders(token),
    }),
  create: (token: string, data: { code: string; name: string; credits?: number; department?: string; semester?: string }) =>
    request("/courses/", { method: "POST", headers: authHeaders(token), body: JSON.stringify(data) }),
  delete: (token: string, courseId: number) =>
    request(`/courses/${courseId}`, { method: "DELETE", headers: authHeaders(token) }),
  enroll: (token: string, courseId: number, studentId: number) =>
    request("/courses/enroll", { method: "POST", headers: authHeaders(token), body: JSON.stringify({ course_id: courseId, student_id: studentId }) }),
  myEnrolled: (token: string) =>
    request<Array<{ id: number; code: string; name: string; credits: number }>>("/courses/enrolled/me", {
      headers: authHeaders(token),
    }),
};

// ── Routines ──
export const routinesApi = {
  mine: (token: string) =>
    request<Array<{ id: number; course_id: number; day_of_week: string; start_time: string; end_time: string; room: string; course_code?: string; course_name?: string }>>("/routines/me", {
      headers: authHeaders(token),
    }),
  forCourse: (token: string, courseId: number) =>
    request<Array<{ id: number; course_id: number; day_of_week: string; start_time: string; end_time: string; room: string }>>(`/routines/course/${courseId}`, {
      headers: authHeaders(token),
    }),
  create: (token: string, data: { course_id: number; day_of_week: string; start_time: string; end_time: string; room: string }) =>
    request("/routines/", { method: "POST", headers: authHeaders(token), body: JSON.stringify(data) }),
  update: (token: string, routineId: number, data: Partial<{ day_of_week: string; start_time: string; end_time: string; room: string }>) =>
    request(`/routines/${routineId}`, { method: "PATCH", headers: authHeaders(token), body: JSON.stringify(data) }),
  delete: (token: string, routineId: number) =>
    request(`/routines/${routineId}`, { method: "DELETE", headers: authHeaders(token) }),
};

// ── Attendance ──
export const attendanceApi = {
  createSession: (token: string, data: { course_id: number; duration_minutes?: number }) =>
    request<{ id: number; course_id: number; qr_code: string; session_date: string; expires_at: string; is_active: boolean }>("/attendance/session", {
      method: "POST",
      headers: authHeaders(token),
      body: JSON.stringify(data),
    }),
  markQR: (token: string, data: { session_id: number; qr_code: string }) =>
    request("/attendance/mark/qr", { method: "POST", headers: authHeaders(token), body: JSON.stringify(data) }),
  stats: (token: string, courseId: number) =>
    request<{ course_id: number; total_classes: number; present: number; absent: number; late: number; percentage: number; can_bunk: number }>(`/attendance/stats/${courseId}`, {
      headers: authHeaders(token),
    }),
};

// ── Results ──
export const resultsApi = {
  submit: (token: string, data: { student_id: number; course_id: number; exam_type: string; marks_obtained: number; total_marks: number }) =>
    request("/results/", { method: "POST", headers: authHeaders(token), body: JSON.stringify(data) }),
  myResults: (token: string) =>
    request<Array<{ id: number; course_id: number; exam_type: string; marks_obtained: number; total_marks: number; grade: string | null; grade_point: number | null }>>("/results/me", {
      headers: authHeaders(token),
    }),
  cgpa: (token: string) =>
    request<{ cgpa: number; total_credits: number; courses: Array<Record<string, unknown>> }>("/results/cgpa", {
      headers: authHeaders(token),
    }),
};

// ── Syllabus ──
export const syllabusApi = {
  forCourse: (token: string, courseId: number) =>
    request<Array<{ id: number; course_id: number; title: string; week_number: number | null; is_completed: boolean }>>(`/syllabus/course/${courseId}`, {
      headers: authHeaders(token),
    }),
  create: (token: string, data: { course_id: number; title: string; week_number?: number }) =>
    request("/syllabus/", { method: "POST", headers: authHeaders(token), body: JSON.stringify(data) }),
  toggleComplete: (token: string, topicId: number) =>
    request(`/syllabus/${topicId}/complete`, { method: "PATCH", headers: authHeaders(token) }),
};

// ── Notifications ──
export const notificationsApi = {
  list: (token: string) =>
    request<Array<{ id: number; title: string; message: string; is_read: boolean; created_at: string }>>("/notifications/me", {
      headers: authHeaders(token),
    }),
  markRead: (token: string, id: number) =>
    request(`/notifications/${id}/read`, { method: "PATCH", headers: authHeaders(token) }),
};

// ── AI Assistant ──
export const assistantApi = {
  chat: (token: string, message: string) =>
    request<{ reply: string; query_type?: string }>("/assistant/chat", {
      method: "POST",
      headers: authHeaders(token),
      body: JSON.stringify({ message }),
    }),
};
