"use client";
import { useEffect, useState } from "react";
import { useAuth } from "@/lib/auth";
import { useRouter } from "next/navigation";
import Navbar from "@/components/Navbar";
import Card from "@/components/ui/Card";
import Badge from "@/components/ui/Badge";
import EmptyState from "@/components/ui/EmptyState";
import { useToast } from "@/components/ui/Toast";
import { notificationsApi } from "@/lib/api";
import { Bell } from "lucide-react";

interface Notification { id: number; title: string; message: string; is_read: boolean; created_at: string }

export default function NotificationsPage() {
  const { token, isAuthenticated } = useAuth();
  const router = useRouter();
  const { toast } = useToast();
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!isAuthenticated) { router.push("/login"); return; }
    if (!token) return;
    const fetch = async () => {
      try {
        const data = await notificationsApi.list(token);
        setNotifications(data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetch();
  }, [token, isAuthenticated, router]);

  if (!isAuthenticated) return null;

  const markRead = async (id: number) => {
    if (!token) return;
    try {
      await notificationsApi.markRead(token, id);
      setNotifications((prev) => prev.map((n) => (n.id === id ? { ...n, is_read: true } : n)));
    } catch (err) {
      toast("error", (err as Error).message);
    }
  };

  return (
    <div className="min-h-screen">
      <Navbar />
      <main className="max-w-2xl mx-auto px-4 py-8 animate-fade-in">
        <h1 className="text-xl font-bold mb-6">Notifications</h1>

        {loading ? (
          <p className="text-xs text-text-muted">Loading...</p>
        ) : notifications.length === 0 ? (
          <EmptyState icon={<Bell size={32} />} title="No notifications" description="You're all caught up." />
        ) : (
          <div className="space-y-3">
            {notifications.map((n) => (
              <Card
                key={n.id}
                hover={!n.is_read}
                onClick={() => !n.is_read && markRead(n.id)}
                className={!n.is_read ? "border-l-2 border-l-primary" : "opacity-60"}
              >
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <p className="text-sm font-medium">{n.title}</p>
                    <p className="text-xs text-text-muted mt-1">{n.message}</p>
                    <p className="text-xs text-text-muted/50 mt-2">{new Date(n.created_at).toLocaleDateString()}</p>
                  </div>
                  {!n.is_read && <Badge variant="primary">New</Badge>}
                </div>
              </Card>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
