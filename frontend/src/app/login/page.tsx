"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { authApi } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { useToast } from "@/components/ui/Toast";
import Button from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { GraduationCap } from "lucide-react";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const { toast } = useToast();
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email || !password) return toast("error", "Fill in all fields");
    setLoading(true);
    try {
      const res = await authApi.login({ email, password });
      login(res.access_token, res.user);
      toast("success", `Welcome back, ${res.user.name}`);
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
          <h1 className="text-xl font-bold">Welcome back</h1>
          <p className="text-xs text-text-muted mt-1">Sign in to Campus Mind</p>
        </div>
        <form onSubmit={handleSubmit} className="bg-surface border border-glass-border rounded-lg p-6 space-y-4">
          <Input label="Email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="you@university.edu" />
          <Input label="Password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="••••••••" />
          <Button type="submit" loading={loading} className="w-full">Sign In</Button>
        </form>
        <p className="text-center text-xs text-text-muted mt-4">
          Don&apos;t have an account?{" "}
          <Link href="/register" className="text-primary hover:underline">Register</Link>
        </p>
      </div>
    </div>
  );
}
