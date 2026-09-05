"use client";
import { useState, useRef, useEffect } from "react";
import { useAuth } from "@/lib/auth";
import { useRouter } from "next/navigation";
import { assistantApi } from "@/lib/api";

interface Message {
  role: "user" | "assistant";
  text: string;
}

const SUGGESTIONS = [
  "আমার কাল কি ক্লাস?",
  "amar attendance koto?",
  "CSE-301 er teacher ke?",
  "amar cgpa koto?",
  "next class kokhon?",
  "amar result dekhao",
];

export default function AssistantPage() {
  const { token, loading: authLoading } = useAuth();
  const router = useRouter();
  const [messages, setMessages] = useState<Message[]>([
    { role: "assistant", text: "হ্যালো! 👋 আমি CampusMind AI Assistant. বাংলায় বা ইংরেজিতে প্রশ্ন করুন। যেমন: 'আমার কাল কি ক্লাস?' বা 'amar attendance koto?'" },
  ]);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!authLoading && !token) router.push("/login");
  }, [token, authLoading, router]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const send = async (text?: string) => {
    const msg = text || input.trim();
    if (!msg || !token) return;
    setInput("");
    setMessages((prev) => [...prev, { role: "user", text: msg }]);
    setSending(true);
    try {
      const res = await assistantApi.chat(token, msg);
      setMessages((prev) => [...prev, { role: "assistant", text: res.reply }]);
    } catch (err: any) {
      setMessages((prev) => [...prev, { role: "assistant", text: `Error: ${err.message}` }]);
    } finally {
      setSending(false);
    }
  };

  if (authLoading) return <div className="text-center py-20 text-gray-400">Loading...</div>;

  return (
    <div className="max-w-3xl mx-auto">
      <h1 className="text-2xl font-bold mb-6">🤖 AI Assistant</h1>

      {/* Chat Area */}
      <div className="bg-white rounded-xl shadow-sm border min-h-[400px] flex flex-col">
        <div className="flex-1 p-4 space-y-4 overflow-y-auto max-h-[500px]">
          {messages.map((m, i) => (
            <div key={i} className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}>
              <div className={`max-w-[80%] px-4 py-3 rounded-2xl text-sm leading-relaxed ${
                m.role === "user"
                  ? "bg-indigo-600 text-white rounded-br-md"
                  : "bg-gray-100 text-gray-800 rounded-bl-md"
              }`}>
                {m.text}
              </div>
            </div>
          ))}
          {sending && (
            <div className="flex justify-start">
              <div className="bg-gray-100 px-4 py-3 rounded-2xl rounded-bl-md text-sm text-gray-400 animate-pulse">
                Thinking...
              </div>
            </div>
          )}
          <div ref={bottomRef} />
        </div>

        {/* Suggestions */}
        <div className="px-4 py-2 flex gap-2 overflow-x-auto border-t">
          {SUGGESTIONS.map((s) => (
            <button key={s} onClick={() => send(s)} disabled={sending}
              className="whitespace-nowrap text-xs bg-indigo-50 text-indigo-700 px-3 py-1.5 rounded-full hover:bg-indigo-100 transition disabled:opacity-50">
              {s}
            </button>
          ))}
        </div>

        {/* Input */}
        <div className="p-4 border-t flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && send()}
            placeholder="Ask in Bangla or English..."
            className="flex-1 border rounded-lg px-4 py-2 focus:ring-2 focus:ring-indigo-500 outline-none text-sm"
          />
          <button onClick={() => send()} disabled={sending || !input.trim()}
            className="bg-indigo-600 text-white px-6 py-2 rounded-lg hover:bg-indigo-700 transition disabled:opacity-50 text-sm font-medium">
            Send
          </button>
        </div>
      </div>
    </div>
  );
}
