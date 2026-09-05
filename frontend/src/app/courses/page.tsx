"use client";
import { useEffect, useState } from "react";
import { useAuth } from "@/lib/auth";
import { useRouter } from "next/navigation";
import Navbar from "@/components/Navbar";
import Card from "@/components/ui/Card";
import Button from "@/components/ui/Button";
import Badge from "@/components/ui/Badge";
import EmptyState from "@/components/ui/EmptyState";
import { useToast } from "@/components/ui/Toast";
import { coursesApi } from "@/lib/api";
import { BookOpen, Plus } from "lucide-react";

interface Course { id: number; code: string; name: string; credits: number; department?: string; semester?: string }

export default function CoursesPage() {
  const { token, user, isAuthenticated } = useAuth();
  const router = useRouter();
  const { toast } = useToast();
  const [catalog, setCatalog] = useState<Course[]>([]);
  const [enrolled, setEnrolled] = useState<Course[]>([]);
  const [loading, setLoading] = useState(true);
  const [enrolling, setEnrolling] = useState<number | null>(null);

  useEffect(() => {
    if (!isAuthenticated) { router.push("/login"); return; }
    if (!token) return;
    const fetch = async () => {
      try {
        const [cat, enr] = await Promise.all([
          coursesApi.catalog(token),
          coursesApi.myEnrolled(token),
        ]);
        setCatalog(cat);
        setEnrolled(enr);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetch();
  }, [token, isAuthenticated, router]);

  if (!isAuthenticated) return null;

  const enrolledIds = new Set(enrolled.map((c) => c.id));
  const available = catalog.filter((c) => !enrolledIds.has(c.id));

  const handleEnroll = async (courseId: number) => {
    if (!token || !user) return;
    setEnrolling(courseId);
    try {
      await coursesApi.enroll(token, courseId, user.id);
      toast("success", "Enrolled successfully");
      const enr = await coursesApi.myEnrolled(token);
      setEnrolled(enr);
    } catch (err) {
      toast("error", (err as Error).message);
    } finally {
      setEnrolling(null);
    }
  };

  return (
    <div className="min-h-screen">
      <Navbar />
      <main className="max-w-6xl mx-auto px-4 py-8 animate-fade-in">
        <h1 className="text-xl font-bold mb-6">Courses</h1>

        {/* Enrolled */}
        <section className="mb-8">
          <h2 className="text-sm font-semibold mb-3">Enrolled</h2>
          {enrolled.length === 0 ? (
            <p className="text-xs text-text-muted">Not enrolled in any courses yet.</p>
          ) : (
            <div className="grid md:grid-cols-2 gap-3">
              {enrolled.map((c) => (
                <Card key={c.id} className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium">{c.code}</p>
                    <p className="text-xs text-text-muted">{c.name}</p>
                  </div>
                  <Badge variant="success">Enrolled</Badge>
                </Card>
              ))}
            </div>
          )}
        </section>

        {/* Available */}
        <section>
          <h2 className="text-sm font-semibold mb-3">Available Courses</h2>
          {loading ? (
            <p className="text-xs text-text-muted">Loading...</p>
          ) : available.length === 0 ? (
            <EmptyState icon={<BookOpen size={32} />} title="No courses available" description="Check back later or ask your teacher to add courses." />
          ) : (
            <div className="grid md:grid-cols-2 gap-3">
              {available.map((c) => (
                <Card key={c.id} className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium">{c.code}</p>
                    <p className="text-xs text-text-muted">{c.name}</p>
                    <p className="text-xs text-text-muted/60 mt-0.5">{c.credits} credits {c.semester && `• ${c.semester}`}</p>
                  </div>
                  <Button size="sm" variant="secondary" loading={enrolling === c.id} onClick={() => handleEnroll(c.id)}>
                    <Plus size={14} /> Enroll
                  </Button>
                </Card>
              ))}
            </div>
          )}
        </section>
      </main>
    </div>
  );
}
