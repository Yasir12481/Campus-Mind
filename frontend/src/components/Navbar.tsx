"use client";
import Link from "next/link";
import { useAuth } from "@/lib/auth";

export default function Navbar() {
  const { user, logout, loading } = useAuth();

  if (loading) return <nav className="bg-indigo-700 text-white px-6 py-3 h-14" />;

  return (
    <nav className="bg-indigo-700 text-white px-6 py-3 flex items-center justify-between shadow-md">
      <Link href="/" className="text-xl font-bold tracking-tight">🎓 CampusMind</Link>

      <div className="flex items-center gap-4 text-sm">
        {user ? (
          <>
            <span className="opacity-80">{user.name} ({user.role})</span>
            {user.role === "student" && (
              <>
                <Link href="/dashboard" className="hover:text-indigo-200">Dashboard</Link>
                <Link href="/assistant" className="hover:text-indigo-200">AI Chat</Link>
              </>
            )}
            {user.role === "teacher" && (
              <>
                <Link href="/teacher" className="hover:text-indigo-200">Teacher Panel</Link>
              </>
            )}
            <button onClick={logout} className="bg-indigo-800 px-3 py-1 rounded hover:bg-indigo-900 transition">
              Logout
            </button>
          </>
        ) : (
          <>
            <Link href="/login" className="hover:text-indigo-200">Login</Link>
            <Link href="/register" className="bg-white text-indigo-700 px-3 py-1 rounded font-medium hover:bg-indigo-50 transition">
              Register
            </Link>
          </>
        )}
      </div>
    </nav>
  );
}
