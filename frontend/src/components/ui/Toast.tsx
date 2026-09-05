"use client";
import { createContext, useContext, useState, useCallback, ReactNode } from "react";
import { CheckCircle, XCircle, Info, AlertTriangle, X } from "lucide-react";

type ToastType = "success" | "error" | "info" | "warning";

interface Toast {
  id: number;
  type: ToastType;
  message: string;
}

interface ToastContextValue {
  toast: (type: ToastType, message: string) => void;
}

const ToastContext = createContext<ToastContextValue>({ toast: () => {} });

export function useToast() {
  return useContext(ToastContext);
}

const icons = {
  success: CheckCircle,
  error: XCircle,
  info: Info,
  warning: AlertTriangle,
};

const colors = {
  success: "border-success/30 bg-success/10",
  error: "border-danger/30 bg-danger/10",
  info: "border-primary/30 bg-primary/10",
  warning: "border-warning/30 bg-warning/10",
};

let id = 0;

export function ToastProvider({ children }: { children: ReactNode }) {
  const [toasts, setToasts] = useState<Toast[]>([]);

  const toast = useCallback((type: ToastType, message: string) => {
    const t = { id: ++id, type, message };
    setToasts((prev) => [...prev, t]);
    setTimeout(() => {
      setToasts((prev) => prev.filter((x) => x.id !== t.id));
    }, 4000);
  }, []);

  const dismiss = (tid: number) => {
    setToasts((prev) => prev.filter((x) => x.id !== tid));
  };

  return (
    <ToastContext.Provider value={{ toast }}>
      {children}
      <div className="fixed bottom-4 right-4 z-[999] flex flex-col gap-2 max-w-sm">
        {toasts.map((t) => {
          const Icon = icons[t.type];
          return (
            <div
              key={t.id}
              className={`flex items-center gap-3 px-4 py-3 rounded-lg border backdrop-blur-md shadow-lg [animation:toast-in_0.25s_ease-out] ${colors[t.type]}`}
            >
              <Icon size={18} className="shrink-0" />
              <span className="text-sm flex-1">{t.message}</span>
              <button onClick={() => dismiss(t.id)} className="text-text-muted hover:text-text transition-colors">
                <X size={14} />
              </button>
            </div>
          );
        })}
      </div>
    </ToastContext.Provider>
  );
}
