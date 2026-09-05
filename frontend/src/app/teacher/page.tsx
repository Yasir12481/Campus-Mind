"use client";
import { useEffect, useState } from "react";
import { useAuth } from "@/lib/auth";
import { useRouter } from "next/navigation";
import { coursesApi, attendanceApi } from "@/lib/api";

export default function TeacherPanel() {
  const { user, token, loading: authLoading } = useAuth();
  const router = useRouter();
  const [courses, setCourses] = useState<any[]>([]);
  const [activeSession, setActiveSession] = useState<any>(null);
  const [selectedCourse, setSelectedCourse] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (authLoading) return;
    if (!token) { router.push("/login"); return; }
    if (user?.role !== "teacher") { router.push("/dashboard"); return; }
    coursesApi.list(token).then(setCourses).catch(() => []).finally(() => setLoading(false));
  }, [token, user, authLoading, router]);

  const startAttendance = async () => {
    if (!token || !selectedCourse) return;
    try {
      const session = await attendanceApi.createSession(token, selectedCourse);
      setActiveSession(session);
    } catch (err: any) {
      alert(err.message);
    }
  };

  if (authLoading || loading) return <div className="text-center py-20 text-gray-400">Loading...</div>;

  return (
    <div>
      <h1 className="text-3xl font-bold mb-8">👨‍🏫 Teacher Panel</h1>

      <div className="grid md:grid-cols-2 gap-6">
        <div className="bg-white p-6 rounded-xl shadow-sm border">
          <h2 className="font-bold text-lg mb-4">📚 My Courses</h2>
          {courses.length === 0 ? (
            <p className="text-gray-400 text-sm">No courses assigned yet.</p>
          ) : (
            <div className="space-y-2">
              {courses.map((c: any) => (
                <div key={c.id} className={`flex justify-between items-center py-3 px-4 rounded-lg cursor-pointer border transition ${
                  selectedCourse === c.id ? "border-indigo-500 bg-indigo-50" : "border-gray-200 hover:border-indigo-300"
                }`} onClick={() => setSelectedCourse(c.id)}>
                  <span className="font-medium">{c.code}</span>
                  <span className="text-sm text-gray-500">{c.name}</span>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="bg-white p-6 rounded-xl shadow-sm border">
          <h2 className="font-bold text-lg mb-4">📸 Attendance Session</h2>
          {!selectedCourse ? (
            <p className="text-gray-400 text-sm">Select a course to start attendance.</p>
          ) : activeSession ? (
            <div className="space-y-4">
              <div className="bg-green-50 border border-green-200 p-4 rounded-lg">
                <div className="font-bold text-green-700 mb-1">✅ Session Active</div>
                <div className="text-sm text-green-600">QR Code: <code className="bg-white px-2 py-1 rounded font-mono text-lg">{activeSession.qr_code}</code></div>
                <div className="text-xs text-green-500 mt-2">Expires: {new Date(activeSession.expires_at).toLocaleTimeString()}</div>
              </div>
              <p className="text-sm text-gray-500">Share this QR code with students. They can scan or enter it manually.</p>
              <button onClick={() => setActiveSession(null)} className="text-sm text-red-500 hover:underline">End Session</button>
            </div>
          ) : (
            <div className="space-y-4">
              <p className="text-sm text-gray-600">Start an attendance session for <strong>{courses.find(c => c.id === selectedCourse)?.code}</strong></p>
              <button onClick={startAttendance}
                className="w-full bg-indigo-600 text-white py-3 rounded-lg hover:bg-indigo-700 transition font-medium">
                🚀 Start Attendance Session
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
