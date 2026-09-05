"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth";

export default function LoginPage() {
  const { login } = useAuth();
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await login(email, password);
      router.push("/dashboard");
    } catch (err: any) {
      setError(err.message || "Login failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-md mx-auto mt-16">
      <h1 className="text-3xl font-bold mb-8 text-center">Login to CampusMind</h1>
      <form onSubmit={handleSubmit} className="bg-white p-8 rounded-xl shadow-sm border space-y-4">
        {error && <div className="bg-red-50 text-red-600 p-3 rounded text-sm">{error}</div>}
        <div>
          <label className="block text-sm font-medium mb-1">Email</label>
          <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required
            className="w-full border rounded-lg px-4 py-2 focus:ring-2 focus:ring-indigo-500 outline-none" />
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Password</label>
          <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required
            className="w-full border rounded-lg px-4 py-2 focus:ring-2 focus:ring-indigo-500 outline-none" />
        </div>
        <button type="submit" disabled={loading}
          className="w-full bg-indigo-600 text-white py-2 rounded-lg hover:bg-indigo-700 transition disabled:opacity-50">
          {loading ? "Logging in..." : "Login"}
        </button>
      </form>
      <p className="text-center mt-4 text-sm text-gray-600">
        Don&apos;t have an account? <a href="/register" className="text-indigo-600 hover:underline">Register</a>
      </p>
    </div>
  );
}
