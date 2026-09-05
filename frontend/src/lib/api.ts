const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface FetchOptions extends RequestInit {
  token?: string;
}

export async function apiFetch<T>(path: string, options: FetchOptions = {}): Promise<T> {
  const { token, ...fetchOpts } = options;
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(fetchOpts.headers as Record<string, string> || {}),
  };
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const res = await fetch(`${API_BASE}${path}`, { ...fetchOpts, headers });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || "Request failed");
  }

  return res.json();
}

// Auth
export const authApi = {
  register: (data: { name: string; email: string; password: string; role: string; student_id?: string; department?: string }) =>
    apiFetch("/api/v1/auth/register", { method: "POST", body: JSON.stringify(data) }),

  login: (email: string, password: string) =>
    apiFetch<{ access_token: string; token_type: string }>("/api/v1/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    }),

  me: (token: string) =>
    apiFetch<any>("/api/v1/auth/me", { token }),
};

// Courses
export const coursesApi = {
  list: (token: string) => apiFetch<any[]>("/api/v1/courses/", { token }),
  enrolled: (token: string) => apiFetch<any[]>("/api/v1/courses/enrolled/me", { token }),
  create: (token: string, data: any) => apiFetch("/api/v1/courses/", { method: "POST", token, body: JSON.stringify(data) }),
  enroll: (token: string, data: { student_id: number; course_id: number }) =>
    apiFetch("/api/v1/courses/enroll", { method: "POST", token, body: JSON.stringify(data) }),
};

// Routines
export const routinesApi = {
  mine: (token: string) => apiFetch<any[]>("/api/v1/routines/me", { token }),
};

// Attendance
export const attendanceApi = {
  createSession: (token: string, courseId: number, durationMinutes = 15) =>
    apiFetch<any>("/api/v1/attendance/sessions", {
      method: "POST", token,
      body: JSON.stringify({ course_id: courseId, duration_minutes: durationMinutes }),
    }),
  markQR: (token: string, sessionId: number, qrCode: string) =>
    apiFetch("/api/v1/attendance/mark/qr", {
      method: "POST", token,
      body: JSON.stringify({ session_id: sessionId, qr_code: qrCode }),
    }),
  stats: (token: string, courseId: number) =>
    apiFetch<any>(`/api/v1/attendance/course/${courseId}/stats`, { token }),
  mine: (token: string) => apiFetch<any[]>("/api/v1/attendance/me", { token }),
};

// Results
export const resultsApi = {
  mine: (token: string) => apiFetch<any[]>("/api/v1/results/me", { token }),
  cgpa: (token: string) => apiFetch<any>("/api/v1/results/me/cgpa", { token }),
  create: (token: string, data: any) =>
    apiFetch("/api/v1/results/", { method: "POST", token, body: JSON.stringify(data) }),
};

// Assistant
export const assistantApi = {
  chat: (token: string, message: string) =>
    apiFetch<{ reply: string; query_type: string }>("/api/v1/assistant/chat", {
      method: "POST", token,
      body: JSON.stringify({ message }),
    }),
};

// Notifications
export const notificationsApi = {
  mine: (token: string) => apiFetch<any[]>("/api/v1/notifications/me", { token }),
  markRead: (token: string, id: number) =>
    apiFetch(`/api/v1/notifications/${id}/read`, { method: "PATCH", token }),
};
