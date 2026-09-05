"use client";
import { useState } from "react";
import { useAuth } from "@/lib/auth";
import { useRouter } from "next/navigation";
import Navbar from "@/components/Navbar";
import Card from "@/components/ui/Card";
import Button from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { useToast } from "@/components/ui/Toast";
import { attendanceApi } from "@/lib/api";
import { QrCode, CheckCircle } from "lucide-react";

export default function AttendancePage() {
  const { token, isAuthenticated } = useAuth();
  const router = useRouter();
  const { toast } = useToast();
  const [sessionId, setSessionId] = useState("");
  const [qrCode, setQrCode] = useState("");
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);

  if (!isAuthenticated) { router.push("/login"); return null; }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!token) return;
    if (!sessionId || !qrCode) return toast("error", "Enter session ID and QR code");
    setLoading(true);
    try {
      await attendanceApi.markQR(token, { session_id: parseInt(sessionId), qr_code: qrCode });
      setSuccess(true);
      toast("success", "Attendance marked!");
    } catch (err) {
      toast("error", (err as Error).message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen">
      <Navbar />
      <main className="max-w-md mx-auto px-4 py-12 animate-fade-in">
        <div className="text-center mb-8">
          <QrCode size={32} className="text-primary mx-auto mb-3" />
          <h1 className="text-xl font-bold">Mark Attendance</h1>
          <p className="text-xs text-text-muted mt-1">Scan or enter the QR code from your teacher&apos;s screen.</p>
        </div>

        {success ? (
          <Card className="text-center py-8">
            <CheckCircle size={40} className="text-success mx-auto mb-3" />
            <p className="text-sm font-medium">Attendance marked successfully</p>
            <Button variant="ghost" size="sm" className="mt-4" onClick={() => { setSuccess(false); setSessionId(""); setQrCode(""); }}>
              Mark Another
            </Button>
          </Card>
        ) : (
          <Card>
            <form onSubmit={handleSubmit} className="space-y-4">
              <Input label="Session ID" type="number" value={sessionId} onChange={(e) => setSessionId(e.target.value)} placeholder="e.g. 12" />
              <Input label="QR Code" value={qrCode} onChange={(e) => setQrCode(e.target.value)} placeholder="Paste QR code value" />
              <Button type="submit" loading={loading} className="w-full">Mark Present</Button>
            </form>
          </Card>
        )}
      </main>
    </div>
  );
}
