"use client";

import { ReactNode } from "react";

interface StatCardProps {
  label: string;
  value: string | number;
  icon?: ReactNode;
  trend?: { value: string; positive: boolean };
  accentColor?: "primary" | "success" | "warning" | "danger" | "info" | "accent";
  loading?: boolean;
}

const ACCENT_MAP = {
  primary: "text-primary bg-primary/10",
  success: "text-success bg-success-bg",
  warning: "text-warning bg-warning-bg",
  danger: "text-danger bg-danger-bg",
  info: "text-info bg-info-bg",
  accent: "text-accent bg-accent/10",
} as const;

export default function StatCard({
  label,
  value,
  icon,
  trend,
  accentColor = "primary",
  loading = false,
}: StatCardProps) {
  if (loading) {
    return (
      <div className="bg-surface border border-border rounded-xl p-6 shadow-sm animate-pulse">
        <div className="h-4 w-24 rounded bg-border mb-3" />
        <div className="h-8 w-16 rounded bg-border" />
      </div>
    );
  }

  const accentCls = ACCENT_MAP[accentColor];

  return (
    <div className="group bg-surface border border-border rounded-xl p-6 shadow-sm hover:shadow-md transition-all duration-200">
      <div className="flex items-start justify-between mb-3">
        <span className="text-sm font-medium text-muted">{label}</span>
        {icon && (
          <span
            className={`inline-flex items-center justify-center w-9 h-9 rounded-lg text-lg ${accentCls} transition-transform group-hover:scale-110`}
          >
            {icon}
          </span>
        )}
      </div>

      <div className="flex items-end gap-2">
        <span className="text-3xl font-bold text-foreground tracking-tight">
          {value}
        </span>
        {trend && (
          <span
            className={`text-xs font-medium mb-1 ${
              trend.positive ? "text-success" : "text-danger"
            }`}
          >
            {trend.value}
          </span>
        )}
      </div>
    </div>
  );
}
