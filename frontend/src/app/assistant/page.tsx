"use client";
import { useState, useRef, useEffect } from "react";
import { useAuth } from "@/lib/auth";
import { useRouter } from "next/navigation";
import Navbar from "@/components/Navbar";
import Button from "@/components/ui/Button";
import { useToast } from "@/components/ui/Toast";
import { assistantApi } from "@/lib/api";
import { Send, Bot, User } from "lucide-react";

interface Message { role: "user" | "ai"; text: string }

export default function AssistantPage() {
  const { token, isAuthenticated } = useAuth();
  const router = useRouter();
  const { toast } = useToast();
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!isAuthenticated) router.push("/login");
  }, [isAuthenticated, router]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  if (!isAuthenticated) return null;

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || !token) return;
    const userMsg = input.trim();
    setInput("");
    setMessages((prev) => [...prev, { role: "user", text: userMsg }]);
    setLoading(true);
    try {
      const res = await assistantApi.chat(token, userMsg);
      setMessages((prev) => [...prev, { role: "ai", text: res.reply }]);
    } catch (err) {
      toast("error", (err as Error).message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col">
      <Navbar />
      <main className="flex-1 max-w-2xl mx-auto w-full px-4 py-6 flex flex-col">
        <h1 className="text-lg font-bold mb-4">AI Assistant</h1>

        <div className="flex-1 overflow-y-auto space-y-4 mb-4">
          {messages.length === 0 && (
            <div className="text-center text-text-muted text-xs py-12">
              Ask me about your attendance, CGPA, routine, or teachers.
              <br />বাংলাতেও জিজ্ঞাসা করতে পারো 😊
            </div>
          )}
          {messages.map((m, i) => (
            <div key={i} className={`flex gap-3 ${m.role === "user" ? "justify-end" : "justify-start"}`}>
              {m.role === "ai" && <Bot size={18} className="text-primary mt-1 shrink-0" />}
              <div className={`max-w-[80%] px-4 py-2.5 rounded-lg text-sm ${m.role === "user" ? "bg-primary/20 text-text" : "bg-surface-2 text-text border border-border"}`}>
                {m.text}
              </div>
              {m.role === "user" && <User size={18} className="text-text-muted mt-1 shrink-0" />}
            </div>
          ))}
          {loading && (
            <div className="flex gap-3">
              <Bot size={18} className="text-primary mt-1" />
              <div className="px-4 py-2.5 rounded-lg bg-surface-2 border border-border text-sm text-text-muted animate-pulse">Thinking...</div>
            </div>
          )}
          <div ref={bottomRef} />
        </div>

        <form onSubmit={handleSend} className="flex gap-2">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask anything about your campus life..."
            className="flex-1 px-4 py-2.5 bg-surface-2 border border-border rounded-lg text-sm text-text placeholder:text-text-muted/50 focus:border-primary focus:ring-1 focus:ring-primary/30 transition-colors"
          />
          <Button type="submit" loading={loading} disabled={!input.trim()}>
            <Send size={16} />
          </Button>
        </form>
      </main>
    </div>
  );
}
