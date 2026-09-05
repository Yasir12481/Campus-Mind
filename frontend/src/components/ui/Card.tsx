import { HTMLAttributes } from "react";

interface CardProps extends HTMLAttributes<HTMLDivElement> {
  hover?: boolean;
}

export default function Card({ hover = false, className = "", children, ...props }: CardProps) {
  return (
    <div
      className={`bg-surface border border-glass-border rounded-lg p-5 shadow-card transition-all duration-200 ${hover ? "hover:border-border-hover hover:shadow-glow cursor-pointer" : ""} ${className}`}
      {...props}
    >
      {children}
    </div>
  );
}
