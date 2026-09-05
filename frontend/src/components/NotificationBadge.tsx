"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useAuth } from "@/lib/auth";
import { notificationsApi } from "@/lib/api";

export default function NotificationBadge() {
  const { token, loading } = useAuth();
  const [unreadCount, setUnreadCount] = useState(0);

  useEffect(() => {
    if (loading || !token) return;

    let cancelled = false;

    async function fetchCount() {
      try {
        const notifs = await notificationsApi.mine(token!);
        if (!cancelled) {
          const unread = Array.isArray(notifs)
            ? notifs.filter((n: { is_read?: boolean }) => !n.is_read).length
            : 0;
          setUnreadCount(unread);
        }
      } catch {
        // Silently fail — badge is non-critical
      }
    }

    fetchCount();
    const interval = setInterval(fetchCount, 30_000); // Poll every 30s

    return () => {
      cancelled = true;
      clearInterval(interval);
    };
  }, [token, loading]);

  if (loading || !token) return null;

  return (
    <Link
      href="/notifications"
      className="relative inline-flex items-center justify-center w-9 h-9 rounded-lg hover:bg-white/10 transition-colors"
      aria-label={`Notifications${unreadCount > 0 ? ` (${unreadCount} unread)` : ""}`}
    >
      {/* Bell icon */}
      <svg
        xmlns="http://www.w3.org/2000/svg"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
        className="w-5 h-5"
      >
        <path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9" />
        <path d="M10.3 21a1.94 1.94 0 0 0 3.4 0" />
      </svg>

      {/* Count dot */}
      {unreadCount > 0 && (
        <span className="absolute -top-0.5 -right-0.5 inline-flex items-center justify-center min-w-[18px] h-[18px] px-1 text-[10px] font-bold leading-none text-white bg-danger rounded-full border-2 border-indigo-700">
          {unreadCount > 99 ? "99+" : unreadCount}
        </span>
      )}
    </Link>
  );
}
