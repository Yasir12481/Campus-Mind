import Link from "next/link";
import { GraduationCap, Brain, QrCode, Calendar, ArrowRight } from "lucide-react";

const features = [
  { icon: Brain, title: "AI Assistant", desc: "Ask about your classes, CGPA, or routine in Bangla or English." },
  { icon: QrCode, title: "Smart Attendance", desc: "QR-based attendance with bunk calculator and real-time stats." },
  { icon: Calendar, title: "Routine & Courses", desc: "Visual timetable, course enrollment, and syllabus tracking." },
];

export default function LandingPage() {
  return (
    <div className="min-h-screen flex flex-col">
      {/* Hero */}
      <header className="relative flex-1 flex items-center justify-center overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-primary/5 via-transparent to-accent/5" />
        <div className="relative text-center px-4 max-w-2xl mx-auto animate-fade-in">
          <div className="inline-flex items-center gap-2 mb-6">
            <GraduationCap size={32} className="text-primary" />
            <span className="text-lg font-bold">Campus Mind</span>
          </div>
          <h1 className="text-3xl md:text-5xl font-bold leading-tight mb-4">
            Your campus life,
            <br />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary to-accent">organized.</span>
          </h1>
          <p className="text-text-muted text-sm md:text-base max-w-md mx-auto mb-8">
            Attendance, routines, results, and an AI assistant that actually understands you.
          </p>
          <div className="flex items-center justify-center gap-3">
            <Link href="/register" className="inline-flex items-center gap-2 px-6 py-3 bg-primary hover:bg-primary-hover text-white rounded-lg font-medium text-sm transition-all shadow-glow">
              Get Started <ArrowRight size={16} />
            </Link>
            <Link href="/login" className="inline-flex items-center gap-2 px-6 py-3 bg-surface-2 border border-border rounded-lg text-sm font-medium hover:border-border-hover transition-all">
              Sign In
            </Link>
          </div>
        </div>
      </header>

      {/* Features */}
      <section className="py-16 px-4">
        <div className="max-w-4xl mx-auto grid md:grid-cols-3 gap-6">
          {features.map(({ icon: Icon, title, desc }) => (
            <div key={title} className="bg-surface border border-glass-border rounded-lg p-6 hover:border-border-hover transition-all">
              <Icon size={24} className="text-primary mb-3" />
              <h3 className="text-sm font-semibold mb-1">{title}</h3>
              <p className="text-xs text-text-muted leading-relaxed">{desc}</p>
            </div>
          ))}
        </div>
      </section>

      <footer className="py-6 text-center text-xs text-text-muted/50 border-t border-glass-border">
        Campus Mind — built for students who'd rather code than attend.
      </footer>
    </div>
  );
}
