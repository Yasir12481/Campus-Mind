"use client";
import { createContext, useContext, useState, useEffect, ReactNode } from "react";
import { authApi } from "@/lib/api";

interface User {
  id: number;
  name: string;
  email: string;
  role: "student" | "teacher" | "admin";
  student_id?: string;
  department?: string;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  login: (email: string, password: string) => Promise<void>;
  register: (data: any) => Promise<void>;
  logout: () => void;
  loading: boolean;
}

const AuthContext = createContext<AuthContextType>({} as AuthContextType);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const stored = localStorage.getItem("campusmind_token");
    if (stored) {
      setToken(stored);
      authApi.me(stored)
        .then((u) => setUser(u))
        .catch(() => {
          localStorage.removeItem("campusmind_token");
          setToken(null);
        })
        .finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, []);

  const login = async (email: string, password: string) => {
    const res = await authApi.login(email, password);
    localStorage.setItem("campusmind_token", res.access_token);
    setToken(res.access_token);
    const u = await authApi.me(res.access_token);
    setUser(u);
  };

  const register = async (data: any) => {
    await authApi.register(data);
  };

  const logout = () => {
    localStorage.removeItem("campusmind_token");
    setToken(null);
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, token, login, register, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);
