"use client";

import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { api } from "@/lib/api";
import { formatDate } from "@/lib/utils";

interface Ticket {
  id: number;
  subject: string;
  message: string;
  status: string;
  created_at: string;
}

export default function SupportPage() {
  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [subject, setSubject] = useState("");
  const [message, setMessage] = useState("");
  const [sent, setSent] = useState(false);

  const load = () => api<Ticket[]>("/support/tickets").then(setTickets).catch(() => {});
  useEffect(() => { load(); }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await api("/support/tickets", { method: "POST", body: JSON.stringify({ subject, message }) });
    setSubject("");
    setMessage("");
    setSent(true);
    load();
  };

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <h1 className="text-2xl font-bold text-[#1B5E3B]">Support & Contact</h1>

      <Card>
        <CardHeader>
          <CardTitle>Contact Us</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="text-sm text-gray-600">
            <p><strong>Email:</strong> support@transafrik.co.za</p>
            <p><strong>Hours:</strong> Mon–Fri, 08:00–17:00 SAST</p>
          </div>
          <form onSubmit={handleSubmit} className="space-y-4">
            {sent && <p className="text-sm text-green-700">Your ticket has been submitted.</p>}
            <div className="space-y-2">
              <Label>Subject</Label>
              <Input value={subject} onChange={(e) => setSubject(e.target.value)} required />
            </div>
            <div className="space-y-2">
              <Label>Message</Label>
              <textarea
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                className="flex min-h-[120px] w-full rounded-md border border-gray-300 px-3 py-2 text-sm"
                required
              />
            </div>
            <Button type="submit">Submit Ticket</Button>
          </form>
        </CardContent>
      </Card>

      <Card>
        <CardHeader><CardTitle>Your Tickets</CardTitle></CardHeader>
        <CardContent>
          {tickets.length === 0 ? (
            <p className="text-sm text-gray-500">No support tickets yet.</p>
          ) : (
            <div className="space-y-3">
              {tickets.map((t) => (
                <div key={t.id} className="rounded-lg border p-3">
                  <div className="flex justify-between">
                    <p className="font-medium">{t.subject}</p>
                    <span className="text-xs text-gray-500">{t.status}</span>
                  </div>
                  <p className="mt-1 text-sm text-gray-600">{t.message}</p>
                  <p className="mt-1 text-xs text-gray-400">{formatDate(t.created_at)}</p>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
