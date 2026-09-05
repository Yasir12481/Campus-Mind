"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useAuth } from "@/lib/auth";
import { GraduationCap, LayoutDashboard, BookOpen, Calendar, MessageSquare, Bell, QrCode, LogOut, Menu, X } from "lucide-react";
import Badge from "@/components/ui/Badge";
import { useState } from "react";

const navLinks = {
  student: [
    { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
    { href: "/courses", label: "Courses", icon: BookOpen },
    { href: "/attendance", label: "Attendance", icon: QrCode },
    { href: "/assistant", label: "Assistant", icon: MessageSquare },
    { href: "/notifications", label: "Alerts", icon: Bell },
  ],
  teacher: [
    { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
    { href: "/teacher", label: "Manage", icon: BookOpen },
    { href: "/assistant", label: "Assistant", icon: MessageSquare },
    { href: "/notifications", label: "Alerts", icon: Bell },
  ],
};

export default function Navbar() {
  const { user, logout, isAuthenticated } = useAuth();
  const pathname = usePathname();
  const [mobileOpen, setMobileOpen] = useState(false);

  if (!isAuthenticated) return null;

  const role = user?.role?.toLowerCase() || "student";
  const links = role === "teacher" || role === "admin" ? navLinks.teacher : navLinks.student;

  return (
    <nav className="sticky top-0 z-40 bg-bg/80 backdrop-blur-xl border-b border-glass-border">
      <div className="max-w-6xl mx-auto px-4 h-14 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Link href="/dashboard" className="flex items-center gap-2">
            <GraduationCap size={22} className="text-primary" />
            <span className="font-semibold text-sm">Campus Mind</span>
          </Link>
          {user && <Badge variant="primary">{user.role}</Badge>}
        </div>

        {/* Desktop nav */}
        <div className="hidden md:flex items-center gap-1">
          {links.map(({ href, label, icon: Icon }) => (
            <Link
              key={href}
              href={href}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-medium transition-colors ${
                pathname === href ? "bg-primary/10 text-primary" : "text-text-muted hover:text-text hover:bg-surface-2"
              }`}
            >
              <Icon size={14} />
              {label}
            </Link>
          ))}
        </div>

        <div className="hidden md:flex items-center gap-2">
          <span className="text-xs text-text-muted">{user?.name}</span>
          <button onClick={logout} className="p-1.5 rounded-md text-text-muted hover:text-danger hover:bg-danger/10 transition-colors">
            <LogOut size={16} />
          </button>
        </div>

        {/* Mobile toggle */}
        <button className="md:hidden p-2 text-text-muted" onClick={() => setMobileOpen(!mobileOpen)}>
          {mobileOpen ? <X size={20} /> : <Menu size={20} />}
        </button>
      </div>

      {/* Mobile menu */}
      {mobileOpen && (
        <div className="md:hidden border-t border-glass-border bg-surface px-4 py-3 animate-fade-in">
          {links.map(({ href, label, icon: Icon }) => (
            <Link
              key={href}
              href={href}
              onClick={() => setMobileOpen(false)}
              className={`flex items-center gap-2 px-3 py-2.5 rounded-md text-sm ${
                pathname === href ? "bg-primary/10 text-primary" : "text-text-muted"
              }`}
            >
              <Icon size={16} />
              {label}
            </Link>
          ))}
          <button onClick={logout} className="flex items-center gap-2 px-3 py-2.5 rounded-md text-sm text-danger mt-1">
            <LogOut size={16} />
            Logout
          </button>
        </div>
      )}
    </nav>
  );
}
