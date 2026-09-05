"use client";
import { useEffect, useState } from "react";
import { useAuth } from "@/lib/auth";
import { useRouter } from "next/navigation";
import Navbar from "@/components/Navbar";
import Card from "@/components/ui/Card";
import Badge from "@/components/ui/Badge";
import EmptyState from "@/components/ui/EmptyState";
import { routinesApi, coursesApi, resultsApi } from "@/lib/api";
import { Calendar, BookOpen, TrendingUp, Clock } from "lucide-react";

interface RoutineItem {
  id: number;
  course_id: number;
  day_of_week: string;
  start_time: string;
  end_time: string;
  room: string;
  course_code?: string;
  course_name?: string;
}

export default function DashboardPage() {
  const { token, user, isAuthenticated } = useAuth();
  const router = useRouter();
  const [routines, setRoutines] = useState<RoutineItem[]>([]);
  const [courses, setCourses] = useState<Array<{ id: number; code: string; name: string; credits: number }>>([]);
  const [cgpa, setCgpa] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!isAuthenticated) {
      router.push("/login");
      return;
    }
    if (!token) return;

    const fetchData = async () => {
      try {
        const routineData = await routinesApi.mine(token);
        setRoutines(routineData);

        if (user?.role?.toLowerCase() === "student") {
          const enrolled = await coursesApi.myEnrolled(token);
          setCourses(enrolled);
          try {
            const cgpaData = await resultsApi.cgpa(token);
            setCgpa(cgpaData.cgpa);
          } catch { /* no results yet */ }
        } else {
          const myCourses = await coursesApi.list(token);
          setCourses(myCourses);
        }
      } catch (err) {
        console.error("Dashboard fetch error:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [token, isAuthenticated, router, user?.role]);

  if (!isAuthenticated) return null;

  const today = new Date().toLocaleDateString("en-US", { weekday: "long" });
  const todayClasses = routines.filter((r) => r.day_of_week === today);

  return (
    <div className="min-h-screen">
      <Navbar />
      <main className="max-w-6xl mx-auto px-4 py-8 animate-fade-in">
        <div className="mb-8">
          <h1 className="text-xl font-bold">Hey, {user?.name?.split(" ")[0]} 👋</h1>
          <p className="text-sm text-text-muted mt-1">Here&apos;s your {today.toLowerCase()} overview.</p>
        </div>

        {/* Stats row */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          <Card>
            <div className="flex items-center gap-3">
              <div className="p-2 bg-primary/10 rounded-md"><BookOpen size={18} className="text-primary" /></div>
              <div>
                <p className="text-lg font-bold">{courses.length}</p>
                <p className="text-xs text-text-muted">Courses</p>
              </div>
            </div>
          </Card>
          <Card>
            <div className="flex items-center gap-3">
              <div className="p-2 bg-accent/10 rounded-md"><Calendar size={18} className="text-accent" /></div>
              <div>
                <p className="text-lg font-bold">{routines.length}</p>
                <p className="text-xs text-text-muted">Weekly Classes</p>
              </div>
            </div>
          </Card>
          <Card>
            <div className="flex items-center gap-3">
              <div className="p-2 bg-success/10 rounded-md"><Clock size={18} className="text-success" /></div>
              <div>
                <p className="text-lg font-bold">{todayClasses.length}</p>
                <p className="text-xs text-text-muted">Today</p>
              </div>
            </div>
          </Card>
          {cgpa !== null && (
            <Card>
              <div className="flex items-center gap-3">
                <div className="p-2 bg-warning/10 rounded-md"><TrendingUp size={18} className="text-warning" /></div>
                <div>
                  <p className="text-lg font-bold">{cgpa.toFixed(2)}</p>
                  <p className="text-xs text-text-muted">CGPA</p>
                </div>
              </div>
            </Card>
          )}
        </div>

        <div className="grid md:grid-cols-2 gap-6">
          {/* Today's schedule */}
          <Card>
            <h2 className="text-sm font-semibold mb-4 flex items-center gap-2">
              <Clock size={16} className="text-primary" /> Today&apos;s Schedule
            </h2>
            {loading ? (
              <p className="text-xs text-text-muted">Loading...</p>
            ) : todayClasses.length === 0 ? (
              <EmptyState icon={<Calendar size={32} />} title="No classes today" description="Enjoy your free day or catch up on study." />
            ) : (
              <div className="space-y-3">
                {todayClasses.map((r) => (
                  <div key={r.id} className="flex items-center justify-between p-3 bg-surface-2 rounded-md border border-border">
                    <div>
                      <p className="text-sm font-medium">{r.course_code || `Course #${r.course_id}`}</p>
                      <p className="text-xs text-text-muted">{r.room}</p>
                    </div>
                    <div className="text-right">
                      <p className="text-xs font-mono text-primary">{r.start_time} – {r.end_time}</p>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </Card>

          {/* Courses list */}
          <Card>
            <h2 className="text-sm font-semibold mb-4 flex items-center gap-2">
              <BookOpen size={16} className="text-accent" /> {user?.role?.toLowerCase() === "student" ? "Enrolled Courses" : "My Courses"}
            </h2>
            {loading ? (
              <p className="text-xs text-text-muted">Loading...</p>
            ) : courses.length === 0 ? (
              <EmptyState icon={<BookOpen size={32} />} title="No courses yet" description={user?.role?.toLowerCase() === "student" ? "Browse the catalog and enroll." : "Create your first course from the Manage panel."} />
            ) : (
              <div className="space-y-2">
                {courses.map((c) => (
                  <div key={c.id} className="flex items-center justify-between p-3 bg-surface-2 rounded-md border border-border">
                    <div>
                      <p className="text-sm font-medium">{c.code}</p>
                      <p className="text-xs text-text-muted">{c.name}</p>
                    </div>
                    <Badge variant="primary">{c.credits} cr</Badge>
                  </div>
                ))}
              </div>
            )}
          </Card>
        </div>
      </main>
    </div>
  );
}
