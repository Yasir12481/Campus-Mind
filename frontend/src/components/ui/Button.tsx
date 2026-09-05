"use client";
import { Loader2 } from "lucide-react";
import { ButtonHTMLAttributes } from "react";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "ghost" | "danger";
  size?: "sm" | "md" | "lg";
  loading?: boolean;
}

const variants = {
  primary: "bg-primary hover:bg-primary-hover text-white shadow-glow",
  secondary: "bg-surface-2 hover:bg-border text-text border border-border",
  ghost: "bg-transparent hover:bg-surface-2 text-text-muted hover:text-text",
  danger: "bg-danger/10 hover:bg-danger/20 text-danger border border-danger/20",
};

const sizes = {
  sm: "px-3 py-1.5 text-xs rounded-sm",
  md: "px-4 py-2 text-sm rounded-md",
  lg: "px-6 py-3 text-base rounded-lg",
};

export default function Button({
  variant = "primary",
  size = "md",
  loading = false,
  disabled,
  children,
  className = "",
  ...props
}: ButtonProps) {
  return (
    <button
      disabled={disabled || loading}
      className={`inline-flex items-center justify-center gap-2 font-medium transition-all duration-200 cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed ${variants[variant]} ${sizes[size]} ${className}`}
      {...props}
    >
      {loading && <Loader2 size={16} className="animate-spin" />}
      {children}
    </button>
  );
}
