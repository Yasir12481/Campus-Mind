"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { authApi } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { useToast } from "@/components/ui/Toast";
import Button from "@/components/ui/Button";
import { Input, Select } from "@/components/ui/Input";
import { GraduationCap } from "lucide-react";

export default function RegisterPage() {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState("student");
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const { toast } = useToast();
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name || !email || !password) return toast("error", "Fill in all fields");
    if (password.length < 6) return toast("error", "Password must be at least 6 characters");
    setLoading(true);
    try {
      const res = await authApi.register({ name, email, password, role });
      login(res.access_token, res.user);
      toast("success", `Account created. Welcome, ${res.user.name}!`);
      router.push("/dashboard");
    } catch (err) {
      toast("error", (err as Error).message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center px-4">
      <div className="w-full max-w-sm animate-fade-in">
        <div className="text-center mb-8">
          <GraduationCap size={32} className="text-primary mx-auto mb-3" />
          <h1 className="text-xl font-bold">Create account</h1>
          <p className="text-xs text-text-muted mt-1">Join Campus Mind</p>
        </div>
        <form onSubmit={handleSubmit} className="bg-surface border border-glass-border rounded-lg p-6 space-y-4">
          <Input label="Full Name" value={name} onChange={(e) => setName(e.target.value)} placeholder="Your name" />
          <Input label="Email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="you@university.edu" />
          <Input label="Password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="Min 6 characters" />
          <Select label="Role" value={role} onChange={(e) => setRole(e.target.value)}>
            <option value="student">Student</option>
            <option value="teacher">Teacher</option>
          </Select>
          <Button type="submit" loading={loading} className="w-full">Create Account</Button>
        </form>
        <p className="text-center text-xs text-text-muted mt-4">
          Already have an account?{" "}
          <Link href="/login" className="text-primary hover:underline">Sign in</Link>
        </p>
      </div>
    </div>
  );
}
