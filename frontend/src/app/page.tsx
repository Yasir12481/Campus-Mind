"use client";
import Link from "next/link";
import { useAuth } from "@/lib/auth";

export default function Home() {
  const { user, loading } = useAuth();

  if (loading) return <div className="text-center py-20 text-gray-400">Loading...</div>;

  if (user) {
    const dashPath = user.role === "teacher" ? "/teacher" : "/dashboard";
    return (
      <div className="text-center py-20">
        <h1 className="text-4xl font-bold mb-4">Welcome back, {user.name}! 👋</h1>
        <p className="text-gray-600 mb-8">Role: {user.role.charAt(0).toUpperCase() + user.role.slice(1)}</p>
        <Link href={dashPath} className="bg-indigo-600 text-white px-6 py-3 rounded-lg text-lg hover:bg-indigo-700 transition">
          Go to Dashboard →
        </Link>
      </div>
    );
  }

  return (
    <div className="text-center py-20">
      <h1 className="text-5xl font-bold mb-6 bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">
        🎓 CampusMind
      </h1>
      <p className="text-xl text-gray-600 mb-10 max-w-2xl mx-auto">
        Smart Campus Management with Face Attendance, AI Assistant in Bangla/English, and Academic Dashboard
      </p>
      <div className="flex gap-4 justify-center">
        <Link href="/login" className="bg-indigo-600 text-white px-8 py-3 rounded-lg text-lg hover:bg-indigo-700 transition">
          Login
        </Link>
        <Link href="/register" className="border-2 border-indigo-600 text-indigo-600 px-8 py-3 rounded-lg text-lg hover:bg-indigo-50 transition">
          Register
        </Link>
      </div>

      <div className="grid md:grid-cols-3 gap-6 mt-16 max-w-4xl mx-auto text-left">
        <div className="bg-white p-6 rounded-xl shadow-sm border">
          <div className="text-3xl mb-3">📸</div>
          <h3 className="font-bold text-lg mb-2">Smart Attendance</h3>
          <p className="text-gray-600 text-sm">Face recognition + QR code fallback. Auto-stats, bunk calculator, CSV export.</p>
        </div>
        <div className="bg-white p-6 rounded-xl shadow-sm border">
          <div className="text-3xl mb-3">🤖</div>
          <h3 className="font-bold text-lg mb-2">AI Assistant</h3>
          <p className="text-gray-600 text-sm">Ask in Bangla or English. &quot;আমার কাল কি ক্লাস?&quot; — get instant answers from your data.</p>
        </div>
        <div className="bg-white p-6 rounded-xl shadow-sm border">
          <div className="text-3xl mb-3">📊</div>
          <h3 className="font-bold text-lg mb-2">Academic Dashboard</h3>
          <p className="text-gray-600 text-sm">Routine, results, CGPA calculator, syllabus tracker — all in one place.</p>
        </div>
      </div>
    </div>
  );
}
