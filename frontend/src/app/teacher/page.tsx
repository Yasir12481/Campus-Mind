"use client";
import { useEffect, useState, useCallback } from "react";
import { useAuth } from "@/lib/auth";
import { useRouter } from "next/navigation";
import Navbar from "@/components/Navbar";
import Card from "@/components/ui/Card";
import Button from "@/components/ui/Button";
import Badge from "@/components/ui/Badge";
import Modal from "@/components/ui/Modal";
import EmptyState from "@/components/ui/EmptyState";
import { Input, Select } from "@/components/ui/Input";
import { useToast } from "@/components/ui/Toast";
import { coursesApi, routinesApi, attendanceApi, resultsApi } from "@/lib/api";
import { Plus, Trash2, Calendar, BookOpen, QrCode, ClipboardList, X } from "lucide-react";
import { QRCodeSVG } from "qrcode.react";

type Tab = "courses" | "routine" | "attendance" | "results";

const DAYS = ["Saturday", "Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday"];

interface Course { id: number; code: string; name: string; credits: number; semester?: string }
interface Routine { id: number; course_id: number; day_of_week: string; start_time: string; end_time: string; room: string }

export default function TeacherPage() {
  const { token, user, isAuthenticated } = useAuth();
  const router = useRouter();
  const { toast } = useToast();
  const [tab, setTab] = useState<Tab>("courses");
  const [courses, setCourses] = useState<Course[]>([]);
  const [routines, setRoutines] = useState<Routine[]>([]);
  const [selectedCourseId, setSelectedCourseId] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);

  // Course form
  const [showCourseModal, setShowCourseModal] = useState(false);
  const [courseForm, setCourseForm] = useState({ code: "", name: "", credits: "3", department: "", semester: "" });

  // Routine form
  const [showRoutineModal, setShowRoutineModal] = useState(false);
  const [routineForm, setRoutineForm] = useState({ day_of_week: "Saturday", start_time: "10:00", end_time: "11:30", room: "" });

  // Attendance
  const [sessionCourseId, setSessionCourseId] = useState<number | null>(null);
  const [activeSession, setActiveSession] = useState<{ id: number; qr_code: string; expires_at: string } | null>(null);

  // Results
  const [resultForm, setResultForm] = useState({ student_id: "", course_id: "", exam_type: "mid", marks_obtained: "", total_marks: "" });

  const fetchCourses = useCallback(async () => {
    if (!token) return;
    try {
      const data = await coursesApi.list(token);
      setCourses(data);
      if (data.length > 0 && !selectedCourseId) setSelectedCourseId(data[0].id);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, [token, selectedCourseId]);

  const fetchRoutines = useCallback(async () => {
    if (!token) return;
    try {
      const data = await routinesApi.mine(token);
      setRoutines(data);
    } catch (err) {
      console.error(err);
    }
  }, [token]);

  useEffect(() => {
    if (!isAuthenticated) { router.push("/login"); return; }
    fetchCourses();
    fetchRoutines();
  }, [isAuthenticated, router, fetchCourses, fetchRoutines]);

  if (!isAuthenticated) return null;

  const filteredRoutines = selectedCourseId ? routines.filter((r) => r.course_id === selectedCourseId) : routines;

  // ── Handlers ──
  const createCourse = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!token) return;
    try {
      await coursesApi.create(token, { code: courseForm.code, name: courseForm.name, credits: parseInt(courseForm.credits) || 3, department: courseForm.department || undefined, semester: courseForm.semester || undefined });
      toast("success", "Course created");
      setShowCourseModal(false);
      setCourseForm({ code: "", name: "", credits: "3", department: "", semester: "" });
      fetchCourses();
    } catch (err) { toast("error", (err as Error).message); }
  };

  const deleteCourse = async (id: number) => {
    if (!token) return;
    try {
      await coursesApi.delete(token, id);
      toast("success", "Course deleted");
      fetchCourses();
    } catch (err) { toast("error", (err as Error).message); }
  };

  const createRoutine = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!token || !selectedCourseId) return;
    try {
      await routinesApi.create(token, { course_id: selectedCourseId, ...routineForm });
      toast("success", "Routine added");
      setShowRoutineModal(false);
      setRoutineForm({ day_of_week: "Saturday", start_time: "10:00", end_time: "11:30", room: "" });
      fetchRoutines();
    } catch (err) { toast("error", (err as Error).message); }
  };

  const deleteRoutine = async (id: number) => {
    if (!token) return;
    try {
      await routinesApi.delete(token, id);
      toast("success", "Routine removed");
      fetchRoutines();
    } catch (err) { toast("error", (err as Error).message); }
  };

  const startSession = async () => {
    if (!token || !sessionCourseId) return toast("error", "Select a course first");
    try {
      const session = await attendanceApi.createSession(token, { course_id: sessionCourseId });
      setActiveSession({ id: session.id, qr_code: session.qr_code, expires_at: session.expires_at });
      toast("success", "Attendance session started");
    } catch (err) { toast("error", (err as Error).message); }
  };

  const submitResult = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!token) return;
    try {
      await resultsApi.submit(token, {
        student_id: parseInt(resultForm.student_id),
        course_id: parseInt(resultForm.course_id),
        exam_type: resultForm.exam_type,
        marks_obtained: parseFloat(resultForm.marks_obtained),
        total_marks: parseFloat(resultForm.total_marks),
      });
      toast("success", "Result submitted");
      setResultForm({ student_id: "", course_id: "", exam_type: "mid", marks_obtained: "", total_marks: "" });
    } catch (err) { toast("error", (err as Error).message); }
  };

  const tabs: { id: Tab; label: string; icon: typeof BookOpen }[] = [
    { id: "courses", label: "Courses", icon: BookOpen },
    { id: "routine", label: "Routine", icon: Calendar },
    { id: "attendance", label: "Attendance", icon: QrCode },
    { id: "results", label: "Results", icon: ClipboardList },
  ];

  return (
    <div className="min-h-screen">
      <Navbar />
      <main className="max-w-6xl mx-auto px-4 py-8 animate-fade-in">
        <h1 className="text-xl font-bold mb-6">Manage</h1>

        {/* Tabs */}
        <div className="flex gap-1 mb-6 bg-surface p-1 rounded-lg w-fit border border-glass-border">
          {tabs.map(({ id, label, icon: Icon }) => (
            <button
              key={id}
              onClick={() => setTab(id)}
              className={`flex items-center gap-1.5 px-4 py-2 rounded-md text-xs font-medium transition-colors ${tab === id ? "bg-primary/10 text-primary" : "text-text-muted hover:text-text"}`}
            >
              <Icon size={14} />
              {label}
            </button>
          ))}
        </div>

        {/* ── COURSES TAB ── */}
        {tab === "courses" && (
          <div>
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-sm font-semibold">Your Courses</h2>
              <Button size="sm" onClick={() => setShowCourseModal(true)}><Plus size={14} /> Add Course</Button>
            </div>
            {courses.length === 0 ? (
              <EmptyState icon={<BookOpen size={32} />} title="No courses yet" description="Create your first course to get started." />
            ) : (
              <div className="grid gap-3">
                {courses.map((c) => (
                  <Card key={c.id} className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium">{c.code} — {c.name}</p>
                      <p className="text-xs text-text-muted">{c.credits} credits {c.semester && `• ${c.semester}`}</p>
                    </div>
                    <button onClick={() => deleteCourse(c.id)} className="p-2 text-text-muted hover:text-danger transition-colors">
                      <Trash2 size={16} />
                    </button>
                  </Card>
                ))}
              </div>
            )}
          </div>
        )}

        {/* ── ROUTINE TAB ── */}
        {tab === "routine" && (
          <div>
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-3">
                <h2 className="text-sm font-semibold">Routine</h2>
                <Select value={selectedCourseId ?? ""} onChange={(e) => setSelectedCourseId(Number(e.target.value))} className="w-48">
                  {courses.map((c) => <option key={c.id} value={c.id}>{c.code}</option>)}
                </Select>
              </div>
              <Button size="sm" onClick={() => setShowRoutineModal(true)} disabled={!selectedCourseId}>
                <Plus size={14} /> Add Slot
              </Button>
            </div>
            {filteredRoutines.length === 0 ? (
              <EmptyState icon={<Calendar size={32} />} title="No routine entries" description="Add class slots for the selected course." />
            ) : (
              <div className="grid gap-3">
                {filteredRoutines.map((r) => (
                  <Card key={r.id} className="flex items-center justify-between">
                    <div className="flex items-center gap-4">
                      <Badge variant="primary">{r.day_of_week}</Badge>
                      <div>
                        <p className="text-sm font-mono">{r.start_time} – {r.end_time}</p>
                        <p className="text-xs text-text-muted">{r.room}</p>
                      </div>
                    </div>
                    <button onClick={() => deleteRoutine(r.id)} className="p-2 text-text-muted hover:text-danger transition-colors">
                      <Trash2 size={16} />
                    </button>
                  </Card>
                ))}
              </div>
            )}
          </div>
        )}

        {/* ── ATTENDANCE TAB ── */}
        {tab === "attendance" && (
          <div>
            <h2 className="text-sm font-semibold mb-4">Start Attendance Session</h2>
            <Card className="max-w-md">
              <div className="space-y-4">
                <Select label="Course" value={sessionCourseId ?? ""} onChange={(e) => setSessionCourseId(Number(e.target.value))}>
                  <option value="">Select course...</option>
                  {courses.map((c) => <option key={c.id} value={c.id}>{c.code} — {c.name}</option>)}
                </Select>
                <Button onClick={startSession} className="w-full" disabled={!sessionCourseId}>
                  <QrCode size={16} /> Start Session
                </Button>
              </div>
            </Card>

            {activeSession && (
              <Card className="max-w-md mt-4">
                <div className="flex flex-col items-center gap-4">
                  <QRCodeSVG value={activeSession.qr_code} size={180} bgColor="transparent" fgColor="#e4e4ef" />
                  <p className="text-xs text-text-muted">Session #{activeSession.id} • Expires: {new Date(activeSession.expires_at).toLocaleTimeString()}</p>
                  <Button variant="ghost" size="sm" onClick={() => setActiveSession(null)}><X size={14} /> End Session</Button>
                </div>
              </Card>
            )}
          </div>
        )}

        {/* ── RESULTS TAB ── */}
        {tab === "results" && (
          <div>
            <h2 className="text-sm font-semibold mb-4">Submit Result</h2>
            <Card className="max-w-md">
              <form onSubmit={submitResult} className="space-y-4">
                <Input label="Student ID" type="number" value={resultForm.student_id} onChange={(e) => setResultForm({ ...resultForm, student_id: e.target.value })} placeholder="e.g. 5" />
                <Select label="Course" value={resultForm.course_id} onChange={(e) => setResultForm({ ...resultForm, course_id: e.target.value })}>
                  <option value="">Select course...</option>
                  {courses.map((c) => <option key={c.id} value={c.id}>{c.code}</option>)}
                </Select>
                <Select label="Exam Type" value={resultForm.exam_type} onChange={(e) => setResultForm({ ...resultForm, exam_type: e.target.value })}>
                  <option value="mid">Mid</option>
                  <option value="final">Final</option>
                  <option value="quiz">Quiz</option>
                  <option value="assignment">Assignment</option>
                </Select>
                <div className="grid grid-cols-2 gap-3">
                  <Input label="Marks" type="number" value={resultForm.marks_obtained} onChange={(e) => setResultForm({ ...resultForm, marks_obtained: e.target.value })} placeholder="35" />
                  <Input label="Total" type="number" value={resultForm.total_marks} onChange={(e) => setResultForm({ ...resultForm, total_marks: e.target.value })} placeholder="50" />
                </div>
                <Button type="submit" className="w-full">Submit Result</Button>
              </form>
            </Card>
          </div>
        )}
      </main>

      {/* ── MODALS ── */}
      <Modal open={showCourseModal} onClose={() => setShowCourseModal(false)} title="Create Course">
        <form onSubmit={createCourse} className="space-y-4">
          <Input label="Code" value={courseForm.code} onChange={(e) => setCourseForm({ ...courseForm, code: e.target.value })} placeholder="CSE-301" />
          <Input label="Name" value={courseForm.name} onChange={(e) => setCourseForm({ ...courseForm, name: e.target.value })} placeholder="Data Structures" />
          <div className="grid grid-cols-2 gap-3">
            <Input label="Credits" type="number" value={courseForm.credits} onChange={(e) => setCourseForm({ ...courseForm, credits: e.target.value })} />
            <Input label="Semester" value={courseForm.semester} onChange={(e) => setCourseForm({ ...courseForm, semester: e.target.value })} placeholder="Fall 2026" />
          </div>
          <Input label="Department" value={courseForm.department} onChange={(e) => setCourseForm({ ...courseForm, department: e.target.value })} placeholder="CSE" />
          <Button type="submit" className="w-full">Create</Button>
        </form>
      </Modal>

      <Modal open={showRoutineModal} onClose={() => setShowRoutineModal(false)} title="Add Routine Slot">
        <form onSubmit={createRoutine} className="space-y-4">
          <Select label="Day" value={routineForm.day_of_week} onChange={(e) => setRoutineForm({ ...routineForm, day_of_week: e.target.value })}>
            {DAYS.map((d) => <option key={d} value={d}>{d}</option>)}
          </Select>
          <div className="grid grid-cols-2 gap-3">
            <Input label="Start" type="time" value={routineForm.start_time} onChange={(e) => setRoutineForm({ ...routineForm, start_time: e.target.value })} />
            <Input label="End" type="time" value={routineForm.end_time} onChange={(e) => setRoutineForm({ ...routineForm, end_time: e.target.value })} />
          </div>
          <Input label="Room" value={routineForm.room} onChange={(e) => setRoutineForm({ ...routineForm, room: e.target.value })} placeholder="Room 204" />
          <Button type="submit" className="w-full">Add Slot</Button>
        </form>
      </Modal>
    </div>
  );
}
