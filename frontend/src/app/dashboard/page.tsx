"use client";
import { useEffect, useState } from "react";
import { useAuth } from "@/lib/auth";
import { useRouter } from "next/navigation";
import { coursesApi, routinesApi, resultsApi, attendanceApi } from "@/lib/api";

export default function StudentDashboard() {
  const { user, token, loading: authLoading } = useAuth();
  const router = useRouter();
  const [courses, setCourses] = useState<any[]>([]);
  const [routines, setRoutines] = useState<any[]>([]);
  const [cgpa, setCgpa] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (authLoading) return;
    if (!token) { router.push("/login"); return; }
    if (user?.role !== "student") { router.push("/teacher"); return; }

    Promise.all([
      coursesApi.enrolled(token).catch(() => []),
      routinesApi.mine(token).catch(() => []),
      resultsApi.cgpa(token).catch(() => null),
    ]).then(([c, r, g]) => {
      setCourses(c);
      setRoutines(r);
      setCgpa(g);
      setLoading(false);
    });
  }, [token, user, authLoading, router]);

  if (authLoading || loading) return <div className="text-center py-20 text-gray-400">Loading dashboard...</div>;

  return (
    <div>
      <h1 className="text-3xl font-bold mb-8">📚 Student Dashboard</h1>

      <div className="grid md:grid-cols-3 gap-6 mb-8">
        <div className="bg-white p-6 rounded-xl shadow-sm border">
          <div className="text-sm text-gray-500 mb-1">Enrolled Courses</div>
          <div className="text-3xl font-bold text-indigo-600">{courses.length}</div>
        </div>
        <div className="bg-white p-6 rounded-xl shadow-sm border">
          <div className="text-sm text-gray-500 mb-1">CGPA</div>
          <div className="text-3xl font-bold text-green-600">{cgpa?.cgpa ?? "N/A"}</div>
        </div>
        <div className="bg-white p-6 rounded-xl shadow-sm border">
          <div className="text-sm text-gray-500 mb-1">Weekly Classes</div>
          <div className="text-3xl font-bold text-purple-600">{routines.length}</div>
        </div>
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        <div className="bg-white p-6 rounded-xl shadow-sm border">
          <h2 className="font-bold text-lg mb-4">📅 My Routine</h2>
          {routines.length === 0 ? (
            <p className="text-gray-400 text-sm">No routine scheduled yet.</p>
          ) : (
            <div className="space-y-2">
              {routines.map((r: any) => (
                <div key={r.id} className="flex justify-between items-center py-2 border-b last:border-0">
                  <span className="font-medium">{r.course_code || `Course #${r.course_id}`}</span>
                  <span className="text-sm text-gray-500">{r.day_of_week} {r.start_time} — Room {r.room}</span>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="bg-white p-6 rounded-xl shadow-sm border">
          <h2 className="font-bold text-lg mb-4">📖 Enrolled Courses</h2>
          {courses.length === 0 ? (
            <p className="text-gray-400 text-sm">Not enrolled in any courses yet.</p>
          ) : (
            <div className="space-y-2">
              {courses.map((c: any) => (
                <div key={c.id} className="flex justify-between items-center py-2 border-b last:border-0">
                  <span className="font-medium">{c.code}</span>
                  <span className="text-sm text-gray-500">{c.name} ({c.credits} cr)</span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
