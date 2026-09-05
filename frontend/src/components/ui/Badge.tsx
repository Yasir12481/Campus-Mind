import { HTMLAttributes } from "react";

interface BadgeProps extends HTMLAttributes<HTMLSpanElement> {
  variant?: "default" | "success" | "warning" | "danger" | "primary";
}

const variants = {
  default: "bg-surface-2 text-text-muted border-border",
  success: "bg-success/10 text-success border-success/20",
  warning: "bg-warning/10 text-warning border-warning/20",
  danger: "bg-danger/10 text-danger border-danger/20",
  primary: "bg-primary/10 text-primary border-primary/20",
};

export default function Badge({ variant = "default", className = "", children, ...props }: BadgeProps) {
  return (
    <span
      className={`inline-flex items-center px-2 py-0.5 text-xs font-medium rounded-full border ${variants[variant]} ${className}`}
      {...props}
    >
      {children}
    </span>
  );
}
