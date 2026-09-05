"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth";

export default function RegisterPage() {
  const { register } = useAuth();
  const router = useRouter();
  const [form, setForm] = useState({ name: "", email: "", password: "", role: "student", student_id: "", department: "" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await register(form);
      router.push("/login");
    } catch (err: any) {
      setError(err.message || "Registration failed");
    } finally {
      setLoading(false);
    }
  };

  const update = (field: string) => (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) =>
    setForm({ ...form, [field]: e.target.value });

  return (
    <div className="max-w-md mx-auto mt-16">
      <h1 className="text-3xl font-bold mb-8 text-center">Create Account</h1>
      <form onSubmit={handleSubmit} className="bg-white p-8 rounded-xl shadow-sm border space-y-4">
        {error && <div className="bg-red-50 text-red-600 p-3 rounded text-sm">{error}</div>}
        <div>
          <label className="block text-sm font-medium mb-1">Full Name</label>
          <input type="text" value={form.name} onChange={update("name")} required
            className="w-full border rounded-lg px-4 py-2 focus:ring-2 focus:ring-indigo-500 outline-none" />
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Email</label>
          <input type="email" value={form.email} onChange={update("email")} required
            className="w-full border rounded-lg px-4 py-2 focus:ring-2 focus:ring-indigo-500 outline-none" />
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Password</label>
          <input type="password" value={form.password} onChange={update("password")} required minLength={6}
            className="w-full border rounded-lg px-4 py-2 focus:ring-2 focus:ring-indigo-500 outline-none" />
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Role</label>
          <select value={form.role} onChange={update("role")}
            className="w-full border rounded-lg px-4 py-2 focus:ring-2 focus:ring-indigo-500 outline-none">
            <option value="student">Student</option>
            <option value="teacher">Teacher</option>
          </select>
        </div>
        {form.role === "student" && (
          <>
            <div>
              <label className="block text-sm font-medium mb-1">Student ID</label>
              <input type="text" value={form.student_id} onChange={update("student_id")} placeholder="CSE-2021-001"
                className="w-full border rounded-lg px-4 py-2 focus:ring-2 focus:ring-indigo-500 outline-none" />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Department</label>
              <input type="text" value={form.department} onChange={update("department")} placeholder="CSE"
                className="w-full border rounded-lg px-4 py-2 focus:ring-2 focus:ring-indigo-500 outline-none" />
            </div>
          </>
        )}
        <button type="submit" disabled={loading}
          className="w-full bg-indigo-600 text-white py-2 rounded-lg hover:bg-indigo-700 transition disabled:opacity-50">
          {loading ? "Creating account..." : "Register"}
        </button>
      </form>
      <p className="text-center mt-4 text-sm text-gray-600">
        Already have an account? <a href="/login" className="text-indigo-600 hover:underline">Login</a>
      </p>
    </div>
  );
}
