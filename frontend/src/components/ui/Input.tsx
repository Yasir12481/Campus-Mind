"use client";
import { InputHTMLAttributes, SelectHTMLAttributes } from "react";

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
}

export function Input({ label, error, className = "", ...props }: InputProps) {
  return (
    <div className="flex flex-col gap-1.5">
      {label && <label className="text-xs font-medium text-text-muted uppercase tracking-wide">{label}</label>}
      <input
        className={`w-full px-3 py-2.5 bg-surface-2 border rounded-md text-sm text-text placeholder:text-text-muted/50 transition-colors focus:border-primary focus:ring-1 focus:ring-primary/30 ${error ? "border-danger" : "border-border"} ${className}`}
        {...props}
      />
      {error && <span className="text-xs text-danger">{error}</span>}
    </div>
  );
}

interface SelectProps extends SelectHTMLAttributes<HTMLSelectElement> {
  label?: string;
  error?: string;
}

export function Select({ label, error, className = "", children, ...props }: SelectProps) {
  return (
    <div className="flex flex-col gap-1.5">
      {label && <label className="text-xs font-medium text-text-muted uppercase tracking-wide">{label}</label>}
      <select
        className={`w-full px-3 py-2.5 bg-surface-2 border rounded-md text-sm text-text transition-colors focus:border-primary focus:ring-1 focus:ring-primary/30 ${error ? "border-danger" : "border-border"} ${className}`}
        {...props}
      >
        {children}
      </select>
      {error && <span className="text-xs text-danger">{error}</span>}
    </div>
  );
}
